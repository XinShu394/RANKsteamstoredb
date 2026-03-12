"""
Steam Crawler Configuration
配置模块 V0.3
"""

from pathlib import Path

# ==================== 基础配置 ====================
# Steam排行榜URL模板
# 示例: https://store.steampowered.com/charts/topsellers/US/2025-12-23
CHARTS_URL_TEMPLATE = "https://store.steampowered.com/charts/topsellers/{region}/{date}"

# 默认设置
DEFAULT_REGION = "US"
DEFAULT_DATE = "2025-12-23"  # 作为一个测试基准日期

# Steam周榜更新基准 (周二 = 1)
# Python weekday: Mon=0, Tue=1, Wed=2 ...
STEAM_WEEK_START_DAY = 1

# ==================== 地区映射 ====================
# 用户输入名称 -> Steam地区代码
REGION_MAP = {
    "全球": "global",
    "中国": "CN",
    "美国": "US",
    "日本": "JP",
    "韩国": "KR",
    "英国": "GB",
    "法国": "FR",
    "德国": "DE",
    "俄罗斯": "RU",
    "巴西": "BR",
}

# 常用地区列表（用于交互提示）
COMMON_REGIONS = ["全球", "中国", "美国", "日本", "韩国"]

# ==================== 请求配置 ====================
# User-Agent列表 (随机选择)
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0"
]

RETRY_CONFIG = {
    "max_retries": 3,
    "delay": 2,          # 基础延迟(秒)
    "backoff_factor": 2  # 指数退避因子
}

# ==================== 存储配置 ====================
# 路径设置
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
LOG_DIR = BASE_DIR / "logs"
DEBUG_HTML_DIR = LOG_DIR

OUTPUT_CONFIG = {
    "output_dir": str(RAW_DATA_DIR),
    "csv_filename_template": "steam_topsellers_{region}_{date}.csv",
    "encoding": "utf-8-sig"  # 带BOM的UTF-8，方便Excel打开
}

# ==================== 日志配置 ====================
LOG_CONFIG = {
    "log_dir": str(LOG_DIR),
    "log_filename": "steam_crawler.log",
    "log_level": "INFO",
    "log_format": "%(asctime)s - %(levelname)s - %(message)s",
    "console_output": True
}
