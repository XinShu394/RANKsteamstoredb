"""
Steam Charts 榜单配置文件
专门用于月度/年度榜单爬虫
与原有的畅销榜爬虫独立
"""

from pathlib import Path

# ==================== 基础配置 ====================
# 月度新品榜单URL模板
# 示例: https://store.steampowered.com/charts/topnewreleases/december_2025
MONTHLY_URL_TEMPLATE = "https://store.steampowered.com/charts/topnewreleases/{month}_{year}"

# 年度榜单URL模板
# 示例: https://store.steampowered.com/charts/bestofyear/2025?tab=2
YEARLY_URL_TEMPLATE = "https://store.steampowered.com/charts/bestofyear/{year}?tab={tab}"

# ==================== 月份映射 ====================
MONTH_MAP = {
    "1": "january",
    "2": "february",
    "3": "march",
    "4": "april",
    "5": "may",
    "6": "june",
    "7": "july",
    "8": "august",
    "9": "september",
    "10": "october",
    "11": "november",
    "12": "december",
    # 支持中文输入
    "一月": "january",
    "二月": "february",
    "三月": "march",
    "四月": "april",
    "五月": "may",
    "六月": "june",
    "七月": "july",
    "八月": "august",
    "九月": "september",
    "十月": "october",
    "十一月": "november",
    "十二月": "december",
}

# ==================== 年度榜单Tab映射 ====================
YEARLY_TAB_MAP = {
    "0": "年度最佳游戏",
    "1": "年度最畅销",
    "2": "年度最多游玩",
    "3": "年度最受好评",
    "4": "年度新晋佳作",
    "5": "年度最佳抢先体验",
}

YEARLY_TAB_EN_MAP = {
    "0": "best_of_year",
    "1": "top_sellers",
    "2": "most_played",
    "3": "best_rated",
    "4": "best_new_release",
    "5": "best_early_access",
}

# 常用快捷选项
YEARLY_TAB_SHORTCUTS = {
    "全部": "all",  # 特殊标记，表示抓取所有tab
    "最畅销": "1",
    "最多玩": "2",
    "最受好评": "3",
}

# ==================== 请求配置 ====================
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]

RETRY_CONFIG = {
    "max_retries": 3,
    "delay": 3,          # 基础延迟(秒)，比畅销榜稍长
    "backoff_factor": 2
}

# 页面加载等待配置
PAGE_LOAD_CONFIG = {
    "wait_time": 5,           # React应用加载等待时间(秒)
    "scroll_wait": 1,         # 滚动后等待时间
    "max_scroll_times": 3,    # 最大滚动次数（加载更多数据）
}

# ==================== 存储配置 ====================
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
CHARTS_DATA_DIR = DATA_DIR / "charts"  # 独立的榜单数据目录
RAW_DATA_DIR = CHARTS_DATA_DIR / "raw"
MONTHLY_BATCH_DIR = CHARTS_DATA_DIR / "monthly"
YEARLY_BATCH_DIR = CHARTS_DATA_DIR / "yearly"
LOG_DIR = BASE_DIR / "logs"

# 自动创建目录
CHARTS_DATA_DIR.mkdir(exist_ok=True, parents=True)
RAW_DATA_DIR.mkdir(exist_ok=True, parents=True)
MONTHLY_BATCH_DIR.mkdir(exist_ok=True, parents=True)
YEARLY_BATCH_DIR.mkdir(exist_ok=True, parents=True)

OUTPUT_CONFIG = {
    "output_dir": str(RAW_DATA_DIR),
    # 月度榜单文件名模板
    "monthly_csv_template": "steam_monthly_{month}_{year}.csv",
    "monthly_excel_template": "steam_monthly_{month}_{year}.xlsx",
    # 年度榜单文件名模板
    "yearly_csv_template": "steam_yearly_{year}_tab{tab}_{tab_name}.csv",
    "yearly_excel_template": "steam_yearly_{year}_tab{tab}_{tab_name}.xlsx",
    "encoding": "utf-8-sig"
}

# ==================== 批量爬取配置 ====================
BATCH_CONFIG = {
    # 月榜爬取起始时间
    "monthly_start_year": 2020,
    "monthly_start_month": 1,
    
    # 年榜爬取起始时间
    "yearly_start_year": 2017,
    
    # 批量输出目录
    "monthly_output_dir": str(MONTHLY_BATCH_DIR),
    "yearly_output_dir": str(YEARLY_BATCH_DIR),
}

# ==================== 日志配置 ====================
LOG_CONFIG = {
    "log_dir": str(LOG_DIR),
    "log_filename": "steam_charts_crawler.log",  # 独立的日志文件
    "log_level": "INFO",
    "log_format": "%(asctime)s - %(levelname)s - %(message)s",
    "console_output": True
}

# ==================== 页面元素选择器 ====================
# 根据HTML结构定义的选择器
SELECTORS = {
    # React根容器
    "react_root": 'div[data-featuretarget="react-root"]',
    
    # 可能的游戏项目选择器（需要实际测试确定）
    "game_items": [
        "div[class*='WeeklyTopNewReleasesTable']",
        "div[class*='YearInReviewCard']",
        "a[href*='/app/']",  # 通用的游戏链接
    ],
    
    # 游戏信息元素
    "game_name": "div[class*='StoreSaleWidgetTitle']",
    "game_link": "a[href*='/app/']",
    "game_price": "div[class*='discount_final_price']",
}

# ==================== 调试配置 ====================
DEBUG_CONFIG = {
    "save_html": True,              # 是否保存HTML快照
    "save_screenshot": True,        # 是否保存截图
    "debug_dir": str(LOG_DIR),      # 调试文件目录
}
