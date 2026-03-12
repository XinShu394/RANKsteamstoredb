"""
Steam畅销榜爬虫 V0.3.0 (交互增强版)
新增：交互式输入、智能日期对齐、多地区支持
创建日期: 2026-01-06
"""

from DrissionPage import ChromiumPage
import pandas as pd
import time
import re
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Tuple

# 导入配置
import config


# ==================== 日志初始化 ====================
def setup_logging():
    """配置日志系统"""
    log_dir = Path(config.LOG_CONFIG["log_dir"])
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / config.LOG_CONFIG["log_filename"]
    
    logger = logging.getLogger("SteamCrawler")
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


# ==================== 智能工具类 ====================
class SmartDateAligner:
    """智能日期对齐器"""
    
    @staticmethod
    def align_to_steam_week(input_date_str: str) -> Tuple[str, str]:
        """
        将输入日期对齐到Steam周榜起始日（周二）
        
        Args:
            input_date_str: 输入日期 "YYYY/MM/DD" 或 "YYYY-MM-DD"
            
        Returns:
            (aligned_date_str, original_date_str)
        """
        try:
            # 统一格式处理
            input_date_str = input_date_str.replace('/', '-')
            date_obj = datetime.strptime(input_date_str, "%Y-%m-%d")
            
            # 计算距离上一个周二的天数
            # weekday(): Mon=0, Tue=1, ... Sun=6
            current_weekday = date_obj.weekday()
            target_weekday = config.STEAM_WEEK_START_DAY  # 1 (Tuesday)
            
            # 计算差值：(当前 - 目标 + 7) % 7 得到过去几天是目标日
            # 例：周三(2) - 周二(1) = 1天前
            # 例：周一(0) - 周二(1) = -1 -> +7 = 6天前
            days_diff = (current_weekday - target_weekday) % 7
            
            aligned_date = date_obj - timedelta(days=days_diff)
            aligned_date_str = aligned_date.strftime("%Y-%m-%d")
            
            return aligned_date_str, date_obj.strftime("%Y-%m-%d")
            
        except ValueError:
            logger.error(f"日期格式错误: {input_date_str}")
            return None, None


# ==================== 核心爬虫类 (V0.2.1 Core) ====================
class SteamChartsCrawler:
    """
    Steam排行榜爬虫（V0.3.0）
    基于V0.2.1核心逻辑，支持外部传入region和date
    """
    
    def __init__(self):
        self.page = None
        self.appid_pattern = re.compile(r'app/(\d+)')
        self.price_pattern = re.compile(r'\$?([\d,]+\.?\d*)')
    
    def _init_browser(self):
        """初始化浏览器"""
        logger.info("正在启动Chrome浏览器...")
        try:
            self.page = ChromiumPage()
            logger.info("✅ 浏览器启动成功")
        except Exception as e:
            logger.error(f"❌ 浏览器启动失败: {e}")
            raise
    
    def crawl(self, region: str = "US", chart_date: str = None):
        """
        爬取Steam排行榜
        """
        if chart_date is None:
            chart_date = config.DEFAULT_DATE
        
        logger.info("=" * 80)
        logger.info(f"🚀 开始爬取任务")
        logger.info(f"🌍 地区: {region}")
        logger.info(f"📅 日期: {chart_date} (Steam周榜)")
        logger.info("=" * 80)
        
        try:
            # 初始化浏览器
            self._init_browser()
            
            # 构建URL
            url = config.CHARTS_URL_TEMPLATE.format(region=region, date=chart_date)
            logger.info(f"正在访问: {url}")
            
            # 打开页面
            self.page.get(url)
            logger.info("页面已加载，等待JavaScript渲染...")
            
            # 等待页面加载（关键！）
            time.sleep(5)  # 等待React渲染
            
            # 🆕 点击"查看全部"按钮，展开完整榜单
            self._click_show_all_button()
            
            # 提取数据
            games = self._extract_games_simple(chart_date, region)
            
            if not games:
                logger.critical("💀 未提取到任何游戏数据！")
                self._save_debug_info()
                return None
            
            logger.info(f"✅ 成功提取 {len(games)} 个游戏")
            
            # 保存数据
            filepath = self._save_to_csv(games, region, chart_date)
            
            logger.info("=" * 80)
            logger.info(f"🎉 爬取完成！共获取 {len(games)} 个游戏数据")
            if filepath:
                logger.info(f"💾 数据已保存至: {filepath}")
            logger.info("=" * 80)
            
            return games
            
        except Exception as e:
            logger.error(f"❌ 爬取失败: {e}", exc_info=True)
            return None
        finally:
            if self.page:
                logger.info("关闭浏览器...")
                self.page.quit()
    
    def _click_show_all_button(self):
        """
        点击"查看全部 100"按钮
        """
        try:
            logger.info("正在查找'查看全部'按钮...")
            buttons = self.page.eles('tag:button')
            
            for button in buttons:
                button_text = button.text.strip()
                if '查看全部' in button_text or 'Show all' in button_text.lower():
                    logger.info(f"✅ 找到按钮: {button_text}")
                    button.click()
                    logger.info("已点击按钮，等待数据加载...")
                    time.sleep(3)
                    return True
            
            logger.warning("⚠️ 未找到'查看全部'按钮，可能已经显示全部数据")
            return False
            
        except Exception as e:
            logger.warning(f"点击按钮失败: {e}")
            return False
    
    def _extract_games_simple(self, chart_date: str, region: str) -> List[Dict]:
        """简化版：直接查找tr元素提取数据"""
        games = []
        logger.info("开始提取游戏数据...")
        
        try:
            all_rows = self.page.eles('tag:tr')
            logger.info(f"找到 {len(all_rows)} 个表格行")
            
            # 过滤出包含游戏数据的tr
            game_rows = []
            for row in all_rows:
                # 检查第3列是否有链接
                cells = row.eles('tag:td')
                if len(cells) >= 3:
                    if cells[2].ele('tag:a'):
                        game_rows.append(row)
            
            logger.info(f"有效游戏行数: {len(game_rows)}")
            
            for idx, row in enumerate(game_rows, 1):
                try:
                    game = self._extract_game_from_row(row, idx, chart_date, region)
                    if game:
                        games.append(game)
                        if idx % 20 == 0:
                            logger.info(f"已提取 {idx} 个游戏...")
                except Exception as e:
                    logger.warning(f"提取第{idx}行失败: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"提取游戏列表失败: {e}", exc_info=True)
        
        return games
    
    def _extract_price_value(self, price_text: str) -> str:
        """提取价格数值"""
        if not price_text:
            return "N/A"
        match = self.price_pattern.search(price_text)
        if match:
            return match.group(1).replace(',', '')
        return price_text.strip()
    
    def _extract_game_from_row(self, row, rank: int, chart_date: str, region: str) -> Dict:
        """从单行提取数据"""
        try:
            cells = row.eles('tag:td')
            if len(cells) < 3:
                return None
            
            # 1. 排名
            rank_text = cells[1].text.strip() if len(cells) > 1 else str(rank)
            
            # 2. 游戏信息 (第3列)
            game_link = None
            game_name = "Unknown"
            appid = "N/A"
            
            name_cell = cells[2]
            links = name_cell.eles('tag:a')
            
            for link in links:
                href = link.attr('href') or ''
                if '/app/' in href:
                    game_link = link
                    # AppID
                    match = self.appid_pattern.search(href)
                    if match:
                        appid = match.group(1)
                    
                    # Game Name (通过class属性检查)
                    all_divs = link.eles('tag:div')
                    for div in all_divs:
                        class_attr = div.attr('class') or ''
                        if '_1n_4-zvf0n4aqGEksbgW9N' in class_attr:
                            game_name = div.text.strip()
                            break
                    
                    # 兜底
                    if game_name == "Unknown":
                        text = link.text.strip()
                        if text:
                            game_name = text
                    
                    break
            
            # 3. 价格信息 (第4列)
            price_data = {"current_price": "N/A", "original_price": "N/A", "discount": "0"}
            if len(cells) >= 4:
                price_cell = cells[3]
                price_text = price_cell.text.strip()
                
                if "免费" in price_text or "Free" in price_text.lower():
                    price_data = {"current_price": "Free", "original_price": "Free", "discount": "0"}
                else:
                    discount_div = price_cell.ele('css:div.cnkoFkzVCby40gJ0jGGS4', timeout=0.1)
                    original_price_div = price_cell.ele('css:div._3fFFsvII7Y2KXNLDk_krOW', timeout=0.1)
                    current_price_div = price_cell.ele('css:div._3j4dI1yA7cRfCvK8h406OB', timeout=0.1)
                    
                    if discount_div and original_price_div and current_price_div:
                        price_data = {
                            "current_price": self._extract_price_value(current_price_div.text),
                            "original_price": self._extract_price_value(original_price_div.text),
                            "discount": discount_div.text.strip()
                        }
                    elif current_price_div:
                        price = self._extract_price_value(current_price_div.text)
                        price_data = {"current_price": price, "original_price": price, "discount": "0"}
                    else:
                        match = self.price_pattern.search(price_text)
                        if match:
                            price = match.group(1).replace(',', '')
                            price_data = {"current_price": price, "original_price": price, "discount": "0"}
            
            return {
                "rank": rank_text,
                "appid": appid,
                "game_name": game_name,
                "current_price": price_data["current_price"],
                "original_price": price_data["original_price"],
                "discount": price_data["discount"],
                "chart_date": chart_date,
                "crawl_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            
        except Exception as e:
            return None
    
    def _save_debug_info(self):
        try:
            debug_dir = Path("logs")
            debug_dir.mkdir(exist_ok=True)
            self.page.get_screenshot(path=str(debug_dir / "debug_error.png"))
        except:
            pass
    
    def _save_to_csv(self, games: List[Dict], region: str, chart_date: str) -> Path:
        if not games:
            return None
        
        output_dir = Path(config.OUTPUT_CONFIG["output_dir"])
        output_dir.mkdir(parents=True, exist_ok=True)
        
        filename = config.OUTPUT_CONFIG["csv_filename_template"].format(
            region=region,
            date=chart_date
        )
        filepath = output_dir / filename
        
        try:
            df = pd.DataFrame(games)
            # 显式移除可能存在的region列（如果字典里不小心带了）
            if 'region' in df.columns:
                df = df.drop(columns=['region'])
                
            df.to_csv(filepath, index=False, encoding=config.OUTPUT_CONFIG["encoding"])
            return filepath
        except Exception as e:
            logger.error(f"❌ 保存CSV失败: {e}")
            return None


# ==================== 交互式启动逻辑 ====================
def interactive_run():
    print("\n" + "="*50)
    print("🎮 Steam 畅销榜爬虫 V0.3.0 (交互增强版)")
    print("="*50 + "\n")
    
    while True:
        # 1. 选择地区
        print("请选择爬取地区:")
        regions = config.COMMON_REGIONS
        for i, r in enumerate(regions, 1):
            print(f"  [{i}] {r}")
        
        region_input = input(f"\n请输入序号或地区代码 (默认 {config.DEFAULT_REGION}): ").strip()
        
        target_region = config.DEFAULT_REGION
        if region_input:
            if region_input.isdigit():
                idx = int(region_input) - 1
                if 0 <= idx < len(regions):
                    cn_name = regions[idx]
                    target_region = config.REGION_MAP.get(cn_name, config.DEFAULT_REGION)
                    print(f"✅ 已选择: {cn_name} ({target_region})")
            else:
                # 尝试直接匹配名称或代码
                if region_input in config.REGION_MAP:
                    target_region = config.REGION_MAP[region_input]
                    print(f"✅ 已选择: {region_input} ({target_region})")
                else:
                    target_region = region_input
                    print(f"⚠️ 使用自定义代码: {target_region}")
        else:
            print(f"✅ 使用默认地区: {target_region}")

        # 2. 选择日期
        print(f"\n请输入查询日期 (格式 YYYY/MM/DD):")
        print(f"⚠️ 注意: Steam周榜每周二更新，系统会自动对齐到最近的周二")
        date_input = input(f"直接回车使用测试日期 ({config.DEFAULT_DATE}): ").strip()
        
        target_date = config.DEFAULT_DATE
        if date_input:
            aligned_date, original_date = SmartDateAligner.align_to_steam_week(date_input)
            if aligned_date:
                target_date = aligned_date
                if aligned_date != original_date:
                    print(f"✅ 智能对齐: {original_date} -> {aligned_date} (周榜起始日)")
                else:
                    print(f"✅ 日期确认: {aligned_date}")
            else:
                print("❌ 日期格式错误，使用默认日期")
        else:
            print(f"✅ 使用默认日期: {target_date}")
        
        # 3. 确认执行
        print("\n" + "-"*30)
        print(f"即将开始爬取:")
        print(f"📍 地区: {target_region}")
        print(f"📅 日期: {target_date}")
        print("-"*30)
        
        confirm = input("\n按回车开始，输入 'n' 取消本次: ").strip().lower()
        if confirm == 'n':
            print("已取消本次任务，重新开始...")
            print("\n" + "-"*50 + "\n")
            continue

        # 4. 执行爬虫
        crawler = SteamChartsCrawler()
        crawler.crawl(region=target_region, chart_date=target_date)
        
        # 5. 询问是否继续
        print("\n" + "="*50)
        choice = input("是否继续爬取其他榜单? (y/n) [默认 n]: ").strip().lower()
        if choice != 'y':
            print("\n👋 感谢使用，再见！")
            break
            
        print("\n" + "="*50 + "\n")  # 分隔符


if __name__ == "__main__":
    try:
        interactive_run()
    except KeyboardInterrupt:
        logger.warning("\n⚠️ 用户中断程序")
    except Exception as e:
        logger.critical(f"\n💀 程序异常退出: {e}", exc_info=True)
    
    input("\n按回车键退出...")

