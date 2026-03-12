"""
Steam Charts 榜单爬虫 V1.0.0
专门用于月度新品榜单和年度榜单
与原有的畅销榜爬虫完全独立

功能：
1. 月度新品榜单 (Top New Releases)
2. 年度榜单 (Best of Year) - 6个不同tab

创建日期: 2026-01-21
"""

from DrissionPage import ChromiumPage, ChromiumOptions
import pandas as pd
import time
import re
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import json

# 导入独立配置
import config_charts as config


# ==================== 日志初始化 ====================
def setup_logging():
    """配置日志系统"""
    log_dir = Path(config.LOG_CONFIG["log_dir"])
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / config.LOG_CONFIG["log_filename"]
    
    logger = logging.getLogger("SteamChartsNewCrawler")
    logger.setLevel(getattr(logging, config.LOG_CONFIG["log_level"]))
    logger.handlers.clear()
    
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(config.LOG_CONFIG["log_format"])
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    if config.LOG_CONFIG["console_output"]:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter('%(levelname)s - %(message)s')
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    
    return logger


logger = setup_logging()


# ==================== 月度榜单爬虫 ====================
class MonthlyNewReleasesCrawler:
    """月度新品榜单爬虫"""
    
    def __init__(self, page: Optional[ChromiumPage] = None):
        self.page = page
        self.appid_pattern = re.compile(r'app/(\d+)')
        self.external_browser = page is not None
        
    def init_browser(self):
        """初始化浏览器"""
        if self.page:
            return True
            
        try:
            co = ChromiumOptions()
            co.headless(False)  # 先不用无头模式，方便调试
            self.page = ChromiumPage(co)
            self.external_browser = False
            logger.info("✅ 浏览器初始化成功")
            return True
        except Exception as e:
            logger.error(f"❌ 浏览器初始化失败: {str(e)}")
            return False
    
    def build_url(self, month: str, year: int) -> str:
        """构建月度榜单URL"""
        # 转换月份
        if month.isdigit() or month in config.MONTH_MAP:
            month_en = config.MONTH_MAP.get(month, month.lower())
        else:
            month_en = month.lower()
        
        url = config.MONTHLY_URL_TEMPLATE.format(
            month=month_en,
            year=year
        )
        logger.info(f"📍 目标URL: {url}")
        return url
    
    def crawl(self, month: str, year: int) -> Optional[pd.DataFrame]:
        """
        爬取月度新品榜单
        
        Args:
            month: 月份 (1-12 或 january-december)
            year: 年份 (2025, 2026等)
            
        Returns:
            DataFrame 或 None
        """
        logger.info(f"🚀 开始爬取 {year}年 {month}月 新品榜单")
        
        # 初始化浏览器
        if not self.init_browser():
            return None
        
        try:
            # 构建URL
            url = self.build_url(month, year)
            
            # 访问页面
            logger.info("📡 正在访问页面...")
            self.page.get(url)
            
            # 等待React应用加载
            logger.info(f"⏳ 等待页面加载 ({config.PAGE_LOAD_CONFIG['wait_time']}秒)...")
            time.sleep(config.PAGE_LOAD_CONFIG['wait_time'])
            
            # 滚动页面，加载更多内容
            self._scroll_page()
            
            # 保存调试信息
            if config.DEBUG_CONFIG["save_html"]:
                self._save_debug_html(f"monthly_{month}_{year}")
            
            # 解析页面
            games_data = self._parse_page()
            
            if not games_data:
                logger.warning("⚠️ 未能提取到游戏数据")
                return None
            
            # 转换为DataFrame
            df = pd.DataFrame(games_data)
            
            # 添加时间列
            df["时间"] = f"{year}-{month}"
            
            logger.info(f"✅ 成功提取 {len(df)} 个游戏")
            
            # 保存数据
            self._save_data(df, month, year)
            
            return df
            
        except Exception as e:
            logger.error(f"❌ 爬取失败: {str(e)}", exc_info=True)
            return None
        finally:
            self._cleanup()
    
    def _scroll_page(self):
        """滚动页面以加载更多内容"""
        for i in range(config.PAGE_LOAD_CONFIG["max_scroll_times"]):
            logger.debug(f"📜 滚动页面 ({i+1}/{config.PAGE_LOAD_CONFIG['max_scroll_times']})")
            self.page.scroll.to_bottom()
            time.sleep(config.PAGE_LOAD_CONFIG["scroll_wait"])
    
    def _parse_page(self) -> List[Dict]:
        """解析页面，提取游戏数据"""
        try:
            logger.info("🔍 正在使用分层策略提取月榜数据...")
            
            headers = []
            
            # 1. 寻找所有的等级标题
            headers = self.page.eles('css:div[class*="SaleSectionHeader"]')
            
            if not headers:
                # 尝试通过关键词寻找
                keywords = ["Platinum", "Gold", "Silver", "Bronze", "铂金", "黄金", "白银", "青铜", "Top", "New"]
                for kw in keywords:
                    found = self.page.eles(f'xpath://div[contains(text(), "{kw}")]')
                    for ele in found:
                        if len(ele.text.strip()) < 20 and ele not in headers:
                            headers.append(ele)

            if headers:
                logger.info(f"📋 找到 {len(headers)} 个等级分组")
                return self._parse_with_tiers(headers)
            
            logger.warning("⚠️ 未找到等级标题，尝试使用备用扁平模式...")
            return self._parse_flat()

        except Exception as e:
            logger.error(f"❌ 页面解析失败: {str(e)}", exc_info=True)
            return []

    def _find_games_for_header(self, header) -> List:
        """为等级标题查找对应的游戏链接"""
        # 策略1: 父容器
        parent = header.parent()
        if parent:
            links = parent.eles('css:a[href*="/app/"]')
            if len(links) >= 1:
                return links
                
        # 策略2: 向上查找更多层级
        curr = header
        for _ in range(3):
            curr = curr.parent()
            if not curr: break
            links = curr.eles('css:a[href*="/app/"]')
            if len(links) >= 1:
                return links
                
        # 策略3: 兄弟容器
        next_ele = header.next()
        if next_ele:
            links = next_ele.eles('css:a[href*="/app/"]')
            if len(links) >= 1:
                return links
                
        return []

    def _parse_with_tiers(self, headers) -> List[Dict]:
        """按等级分组解析"""
        games_data = []
        global_rank = 1
        seen_appids = set()
        
        for header in headers:
            try:
                tier_name = header.text.strip()
                if not tier_name:
                    continue
                    
                logger.info(f"  👉 处理等级: {tier_name}")
                
                # 查找游戏链接
                links = self._find_games_for_header(header)
                
                if not links:
                    logger.warning(f"    ⚠️ 未找到对应的游戏链接")
                    continue
                
                current_tier_games = 0
                for link in links:
                    game_data = self._extract_game_data(link, global_rank, seen_appids)
                    if game_data:
                        game_data["等级"] = tier_name
                        games_data.append(game_data)
                        seen_appids.add(game_data["AppID"])
                        global_rank += 1
                        current_tier_games += 1
                
                logger.info(f"    - 提取到 {current_tier_games} 款游戏")
                
            except Exception as e:
                logger.warning(f"  ⚠️ 处理等级 {header.text} 时出错: {str(e)}")
                continue
                
        return games_data

    def _parse_flat(self) -> List[Dict]:
        """扁平化解析（备用）"""
        games_data = []
        try:
            logger.info("🔍 正在提取游戏数据 (扁平模式)...")
            game_links = self.page.eles('tag:a')
            
            rank = 1
            seen_appids = set()
            
            for link in game_links:
                game_data = self._extract_game_data(link, rank, seen_appids)
                if game_data:
                    game_data["等级"] = "新品榜单" # 默认等级
                    games_data.append(game_data)
                    seen_appids.add(game_data["AppID"])
                    rank += 1
                    
            logger.info(f"✅ 共提取到 {len(games_data)} 个游戏")
        except Exception as e:
            logger.error(f"❌ 页面解析失败: {str(e)}")
        
        return games_data

    def _extract_game_data(self, link, rank, seen_appids) -> Optional[Dict]:
        """提取单个游戏数据"""
        try:
            href = link.attr('href') or ''
            if '/app/' not in href:
                return None
            
            match = self.appid_pattern.search(href)
            if not match:
                return None
            
            appid = match.group(1)
            if appid in seen_appids:
                return None
            
            game_name = self._extract_game_name(link)
            if not game_name:
                return None
                
            return {
                "排名": rank,
                "等级": "", # 占位
                "游戏名称": game_name,
                "AppID": appid,
                "链接": f"https://store.steampowered.com/app/{appid}"
            }
        except:
            return None
    
    def _is_price_text(self, text: str) -> bool:
        """判断文本是否为价格信息"""
        if not text:
            return False
        
        text = text.strip()
        
        # 检查是否以货币符号开头
        price_indicators = ['$', '¥', '€', '£', 'HK$', 'NT$']
        for indicator in price_indicators:
            if text.startswith(indicator):
                return True
        
        # 检查是否包含"免费游玩"等字样
        if text in ['Free', '免费', '免费游玩', 'Free to Play', '免费开玩']:
            return True
        
        return False
    
    def _extract_game_name_from_url(self, url: str) -> Optional[str]:
        """从URL中提取游戏名
        
        Steam URL格式: https://store.steampowered.com/app/{appid}/{game_name}/
        例如: /app/730/CounterStrike_2/ -> Counter-Strike 2
        """
        try:
            from urllib.parse import unquote
            
            # 正则匹配: /app/数字/游戏名/
            match = re.search(r'/app/\d+/([^/?]+)', url)
            if match:
                game_name_slug = match.group(1)
                
                # 处理URL编码的游戏名
                game_name_slug = unquote(game_name_slug)
                
                # 将下划线替换为空格
                game_name = game_name_slug.replace('_', ' ')
                
                return game_name
        except Exception as e:
            logger.debug(f"从URL提取游戏名失败: {str(e)}")
        
        return None
    
    def _extract_game_name(self, link_element) -> Optional[str]:
        """从链接元素中提取游戏名（改进版）"""
        try:
            # 优先尝试查找特定类名的标题元素 (精确匹配)
            name_ele = link_element.ele('css:div[class*="StoreSaleWidgetTitle"]')
            if name_ele:
                return name_ele.text.strip()

            # 其次尝试从图片alt属性获取
            img_ele = link_element.ele('tag:img')
            if img_ele and img_ele.attr('alt'):
                return img_ele.attr('alt').strip()

            # 方法1: 查找子元素中的文本
            text = link_element.text
            if text and len(text.strip()) > 0:
                text = text.strip()
                
                # 过滤价格文本 - 尝试从URL提取
                if self._is_price_text(text):
                    logger.debug(f"跳过价格文本: {text}, 尝试从URL提取")
                    href = link_element.attr('href')
                    if href:
                        name_from_url = self._extract_game_name_from_url(href)
                        if name_from_url:
                            return name_from_url
                    return None
                
                # 过滤折扣信息 (包含%和$)
                if '%' in text and '$' in text:
                    logger.debug(f"跳过折扣信息: {text}")
                    return None
                
                # 过滤评测信息
                if '用户评测' in text or 'reviews' in text.lower() or '评测' in text:
                    logger.debug(f"跳过评测信息: {text}")
                    return None
                
                return text
            
            # 方法2: 查找title属性
            title = link_element.attr('title')
            if title and not self._is_price_text(title):
                return title.strip()
            
            # 方法3: 查找aria-label
            aria_label = link_element.attr('aria-label')
            if aria_label and not self._is_price_text(aria_label):
                return aria_label.strip()
            
            # 方法4: 从URL中提取（最后的备选方案）
            href = link_element.attr('href')
            if href:
                return self._extract_game_name_from_url(href)
            
        except Exception as e:
            logger.debug(f"提取游戏名失败: {str(e)}")
        
        return None
    
    def _save_debug_html(self, prefix: str):
        """保存调试HTML"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"debug_{prefix}_{timestamp}.html"
            filepath = Path(config.DEBUG_CONFIG["debug_dir"]) / filename
            
            html_content = self.page.html
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.debug(f"💾 HTML已保存: {filepath}")
        except Exception as e:
            logger.warning(f"保存HTML失败: {str(e)}")
    
    def _save_data(self, df: pd.DataFrame, month: str, year: int):
        """保存数据到文件"""
        try:
            output_dir = Path(config.OUTPUT_CONFIG["output_dir"])
            output_dir.mkdir(exist_ok=True, parents=True)
            
            # 获取月份英文名
            month_en = config.MONTH_MAP.get(str(month), month)
            
            # CSV文件
            csv_filename = config.OUTPUT_CONFIG["monthly_csv_template"].format(
                month=month_en, year=year
            )
            csv_path = output_dir / csv_filename
            df.to_csv(csv_path, index=False, encoding=config.OUTPUT_CONFIG["encoding"])
            logger.info(f"💾 CSV已保存: {csv_path}")
            
            # Excel文件
            excel_filename = config.OUTPUT_CONFIG["monthly_excel_template"].format(
                month=month_en, year=year
            )
            excel_path = output_dir / excel_filename
            df.to_excel(excel_path, index=False)
            logger.info(f"💾 Excel已保存: {excel_path}")
            
        except Exception as e:
            logger.error(f"❌ 保存数据失败: {str(e)}")
    
    def _cleanup(self):
        """清理资源"""
        try:
            if self.page and not self.external_browser:
                self.page.quit()
                logger.debug("✅ 浏览器已关闭")
        except:
            pass


# ==================== 年度榜单爬虫 ====================
class YearlyBestCrawler:
    """年度榜单爬虫"""
    
    def __init__(self, page: Optional[ChromiumPage] = None):
        self.page = page
        self.appid_pattern = re.compile(r'app/(\d+)')
        self.external_browser = page is not None
    
    def init_browser(self):
        """初始化浏览器"""
        if self.page:
            return True
            
        try:
            co = ChromiumOptions()
            co.headless(False)
            self.page = ChromiumPage(co)
            self.external_browser = False
            logger.info("✅ 浏览器初始化成功")
            return True
        except Exception as e:
            logger.error(f"❌ 浏览器初始化失败: {str(e)}")
            return False
    
    def build_url(self, year: int, tab: int) -> str:
        """构建年度榜单URL"""
        url = config.YEARLY_URL_TEMPLATE.format(year=year, tab=tab)
        tab_name = config.YEARLY_TAB_MAP.get(str(tab), f"Tab{tab}")
        logger.info(f"📍 目标URL: {url} ({tab_name})")
        return url
    
    def crawl(self, year: int, tab: int) -> Optional[pd.DataFrame]:
        """
        爬取年度榜单
        
        Args:
            year: 年份 (2025, 2026等)
            tab: Tab编号 (0-5)
            
        Returns:
            DataFrame 或 None
        """
        tab_name = config.YEARLY_TAB_MAP.get(str(tab), f"Tab{tab}")
        logger.info(f"🚀 开始爬取 {year}年度榜单 - {tab_name}")
        
        if not self.init_browser():
            return None
        
        try:
            url = self.build_url(year, tab)
            
            logger.info("📡 正在访问页面...")
            self.page.get(url)
            
            logger.info(f"⏳ 等待页面加载 ({config.PAGE_LOAD_CONFIG['wait_time']}秒)...")
            time.sleep(config.PAGE_LOAD_CONFIG['wait_time'])
            
            # 滚动页面
            self._scroll_page()
            
            # 保存调试信息
            if config.DEBUG_CONFIG["save_html"]:
                self._save_debug_html(f"yearly_{year}_tab{tab}")
            
            # 解析页面（复用月度爬虫的解析逻辑）
            games_data = self._parse_page()
            
            if not games_data:
                logger.warning("⚠️ 未能提取到游戏数据")
                return None
            
            # 转换为DataFrame
            df = pd.DataFrame(games_data)
            
            # 添加时间列
            df["时间"] = f"{year}"
            
            # --- 强制补全等级逻辑 (防止提取失败) ---
            if "等级" not in df.columns or df["等级"].isnull().all() or (df["等级"] == "").all():
                logger.warning("⚠️ 检测到等级列缺失或为空，正在应用自动推断规则...")
                
                def infer_tier(rank):
                    try:
                        r = int(rank)
                        if r <= 12: return "铂金级"
                        if r <= 24: return "黄金级"
                        if r <= 50: return "白银级"
                        return "青铜级"
                    except:
                        return "入围"
                        
                df["等级"] = df["排名"].apply(infer_tier)
                logger.info("✅ 已自动填充等级列")
            # ---------------------------------------
            
            logger.info(f"✅ 成功提取 {len(df)} 个游戏")
            
            # 保存数据
            self._save_data(df, year, tab)
            
            return df
            
        except Exception as e:
            logger.error(f"❌ 爬取失败: {str(e)}", exc_info=True)
            return None
        finally:
            self._cleanup()
    
    def crawl_all_tabs(self, year: int) -> Dict[int, pd.DataFrame]:
        """爬取所有tab"""
        results = {}
        
        for tab in range(6):
            logger.info(f"\n{'='*70}")
            logger.info(f"正在爬取 Tab {tab}/5")
            logger.info(f"{'='*70}")
            
            df = self.crawl(year, tab)
            if df is not None:
                results[tab] = df
            
            # 间隔等待
            if tab < 5:
                wait_time = 3
                logger.info(f"⏳ 等待 {wait_time} 秒后继续...")
                time.sleep(wait_time)
        
        return results
    
    def _scroll_page(self):
        """滚动页面"""
        for i in range(config.PAGE_LOAD_CONFIG["max_scroll_times"]):
            logger.debug(f"📜 滚动页面 ({i+1}/{config.PAGE_LOAD_CONFIG['max_scroll_times']})")
            self.page.scroll.to_bottom()
            time.sleep(config.PAGE_LOAD_CONFIG["scroll_wait"])
    
    def _parse_page(self) -> List[Dict]:
        """解析页面（支持等级提取）"""
        try:
            logger.info("🔍 正在提取游戏数据...")
            
            headers = []
            
            # 方式1: CSS选择器 (类名包含 SaleSectionHeader)
            headers = self.page.eles('css:div[class*="SaleSectionHeader"]')
            
            # 方式2: 文本匹配
            if not headers:
                keywords = ["Platinum", "Gold", "Silver", "Bronze", "铂金", "黄金", "白银", "青铜"]
                for kw in keywords:
                    eles = self.page.eles(f'xpath://div[contains(text(), "{kw}")]')
                    for ele in eles:
                        if len(ele.text.strip()) < 20 and ele not in headers:
                            headers.append(ele)
                            
            if headers:
                logger.info(f"📋 找到 {len(headers)} 个等级分组")
                return self._parse_with_tiers(headers)
            else:
                logger.info("ℹ️ 未找到等级分组，使用默认模式解析")
                return self._parse_flat()
                
        except Exception as e:
            logger.error(f"❌ 页面解析失败: {str(e)}", exc_info=True)
            return []

    def _find_games_for_header(self, header) -> List:
        """为等级标题查找对应的游戏链接"""
        # 策略1: 父容器
        parent = header.parent()
        if parent:
            links = parent.eles('css:a[href*="/app/"]')
            if len(links) >= 1:
                return links
                
        # 策略2: 向上查找更多层级 (防止 header 被包裹在多层 div 中)
        curr = header
        for _ in range(3):
            curr = curr.parent()
            if not curr: break
            links = curr.eles('css:a[href*="/app/"]')
            if len(links) >= 1:
                return links
                
        # 策略3: 兄弟容器
        next_ele = header.next()
        if next_ele:
            links = next_ele.eles('css:a[href*="/app/"]')
            if len(links) >= 1:
                return links
                
        return []

    def _parse_with_tiers(self, headers) -> List[Dict]:
        """按等级分组解析"""
        games_data = []
        global_rank = 1
        seen_appids = set()
        
        for header in headers:
            try:
                tier_name = header.text.strip()
                if not tier_name:
                    continue
                    
                logger.info(f"  👉 处理等级: {tier_name}")
                
                # 查找游戏链接
                links = self._find_games_for_header(header)
                
                if not links:
                    logger.warning(f"    ⚠️ 未找到对应的游戏链接")
                    continue
                
                current_tier_games = 0
                for link in links:
                    game_data = self._extract_game_data(link, global_rank, seen_appids)
                    if game_data:
                        game_data["等级"] = tier_name
                        games_data.append(game_data)
                        seen_appids.add(game_data["AppID"])
                        global_rank += 1
                        current_tier_games += 1
                
                logger.info(f"    - 提取到 {current_tier_games} 款游戏")
                
            except Exception as e:
                logger.warning(f"  ⚠️ 处理等级 {header.text} 时出错: {str(e)}")
                continue
                
        return games_data

    def _parse_flat(self) -> List[Dict]:
        """扁平化解析（无明确等级时，按位置推断）"""
        games_data = []
        game_links = self.page.eles('tag:a')
        
        rank = 1
        seen_appids = set()
        
        for link in game_links:
            game_data = self._extract_game_data(link, rank, seen_appids)
            if game_data:
                # 兜底策略：按排名推断等级
                # Steam年榜通常规则: 1-12铂金, 13-24黄金, 25-50白银, 51-100青铜
                # 页面通常是按这个顺序展示的
                if rank <= 12:
                    tier = "铂金级"
                elif rank <= 24:
                    tier = "黄金级"
                elif rank <= 50:
                    tier = "白银级"
                else:
                    tier = "青铜级"
                    
                game_data["等级"] = tier
                games_data.append(game_data)
                seen_appids.add(game_data["AppID"])
                rank += 1
                
        return games_data

    def _extract_game_data(self, link, rank, seen_appids) -> Optional[Dict]:
        """提取单个游戏数据"""
        try:
            href = link.attr('href') or ''
            if '/app/' not in href:
                return None
            
            match = self.appid_pattern.search(href)
            if not match:
                return None
            
            appid = match.group(1)
            if appid in seen_appids:
                return None
            
            game_name = self._extract_game_name(link)
            if not game_name:
                return None
                
            # 默认等级逻辑 (根据排名推断)
            # 强制默认等级，确保字段存在
            default_tier = "青铜级"
            if rank <= 12:
                default_tier = "铂金级"
            elif rank <= 24:
                default_tier = "黄金级"
            elif rank <= 50:
                default_tier = "白银级"
            
            return {
                "排名": rank,
                "等级": default_tier,  # 默认赋予等级
                "游戏名称": game_name,
                "AppID": appid,
                "链接": f"https://store.steampowered.com/app/{appid}"
            }
        except:
            return None
    
    def _is_price_text(self, text: str) -> bool:
        """判断文本是否为价格信息"""
        if not text:
            return False
        
        text = text.strip()
        
        # 检查是否以货币符号开头
        price_indicators = ['$', '¥', '€', '£', 'HK$', 'NT$']
        for indicator in price_indicators:
            if text.startswith(indicator):
                return True
        
        # 检查是否包含"免费游玩"等字样
        if text in ['Free', '免费', '免费游玩', 'Free to Play', '免费开玩']:
            return True
        
        return False
    
    def _extract_game_name_from_url(self, url: str) -> Optional[str]:
        """从URL中提取游戏名
        
        Steam URL格式: https://store.steampowered.com/app/{appid}/{game_name}/
        例如: /app/730/CounterStrike_2/ -> Counter-Strike 2
        """
        try:
            from urllib.parse import unquote
            
            # 正则匹配: /app/数字/游戏名/
            match = re.search(r'/app/\d+/([^/?]+)', url)
            if match:
                game_name_slug = match.group(1)
                
                # 处理URL编码的游戏名
                game_name_slug = unquote(game_name_slug)
                
                # 将下划线替换为空格
                game_name = game_name_slug.replace('_', ' ')
                
                return game_name
        except Exception as e:
            logger.debug(f"从URL提取游戏名失败: {str(e)}")
        
        return None
    
    def _extract_game_name(self, link_element) -> Optional[str]:
        """从链接元素中提取游戏名（改进版）"""
        try:
            # 优先尝试查找特定类名的标题元素 (精确匹配)
            name_ele = link_element.ele('css:div[class*="StoreSaleWidgetTitle"]')
            if name_ele:
                return name_ele.text.strip()

            # 其次尝试从图片alt属性获取
            img_ele = link_element.ele('tag:img')
            if img_ele and img_ele.attr('alt'):
                return img_ele.attr('alt').strip()

            # 方法1: 查找子元素中的文本
            text = link_element.text
            if text and len(text.strip()) > 0:
                text = text.strip()
                
                # 过滤价格文本 - 尝试从URL提取
                if self._is_price_text(text):
                    logger.debug(f"跳过价格文本: {text}, 尝试从URL提取")
                    href = link_element.attr('href')
                    if href:
                        name_from_url = self._extract_game_name_from_url(href)
                        if name_from_url:
                            return name_from_url
                    return None
                
                # 过滤折扣信息 (包含%和$)
                if '%' in text and '$' in text:
                    logger.debug(f"跳过折扣信息: {text}")
                    return None
                
                # 过滤评测信息
                if '用户评测' in text or 'reviews' in text.lower() or '评测' in text:
                    logger.debug(f"跳过评测信息: {text}")
                    return None
                
                return text
            
            # 方法2: 查找title属性
            title = link_element.attr('title')
            if title and not self._is_price_text(title):
                return title.strip()
            
            # 方法3: 查找aria-label
            aria_label = link_element.attr('aria-label')
            if aria_label and not self._is_price_text(aria_label):
                return aria_label.strip()
            
            # 方法4: 从URL中提取（最后的备选方案）
            href = link_element.attr('href')
            if href:
                return self._extract_game_name_from_url(href)
            
        except Exception as e:
            logger.debug(f"提取游戏名失败: {str(e)}")
        
        return None
    
    def _save_debug_html(self, prefix: str):
        """保存调试HTML"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"debug_{prefix}_{timestamp}.html"
            filepath = Path(config.DEBUG_CONFIG["debug_dir"]) / filename
            
            html_content = self.page.html
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.debug(f"💾 HTML已保存: {filepath}")
        except Exception as e:
            logger.warning(f"保存HTML失败: {str(e)}")
    
    def _save_data(self, df: pd.DataFrame, year: int, tab: int):
        """保存数据"""
        try:
            output_dir = Path(config.OUTPUT_CONFIG["output_dir"])
            output_dir.mkdir(exist_ok=True, parents=True)
            
            tab_name_en = config.YEARLY_TAB_EN_MAP.get(str(tab), f"tab{tab}")
            
            # CSV
            csv_filename = config.OUTPUT_CONFIG["yearly_csv_template"].format(
                year=year, tab=tab, tab_name=tab_name_en
            )
            csv_path = output_dir / csv_filename
            df.to_csv(csv_path, index=False, encoding=config.OUTPUT_CONFIG["encoding"])
            logger.info(f"💾 CSV已保存: {csv_path}")
            
            # Excel
            excel_filename = config.OUTPUT_CONFIG["yearly_excel_template"].format(
                year=year, tab=tab, tab_name=tab_name_en
            )
            excel_path = output_dir / excel_filename
            df.to_excel(excel_path, index=False)
            logger.info(f"💾 Excel已保存: {excel_path}")
            
        except Exception as e:
            logger.error(f"❌ 保存数据失败: {str(e)}")
    
    def _cleanup(self):
        """清理资源"""
        try:
            if self.page and not self.external_browser:
                self.page.quit()
                logger.debug("✅ 浏览器已关闭")
        except:
            pass


# ==================== 主函数 ====================
if __name__ == "__main__":
    print("=" * 70)
    print("           Steam Charts 榜单爬虫 V1.0.0")
    print("=" * 70)
    print("\n本工具用于爬取：")
    print("  1. 月度新品榜单 (Top New Releases)")
    print("  2. 年度榜单 (Best of Year)")
    print("\n⚠️ 这是独立的爬虫，不影响原有的畅销榜功能")
    print("=" * 70)
    
    input("\n按回车键退出...")
