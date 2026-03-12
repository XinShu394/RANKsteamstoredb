# Steam畅销榜爬虫 V0.1.0

## 📋 项目简介

这是一个自动化爬取Steam畅销榜Top 100数据的爬虫系统，严格遵循**三层架构**设计原则：

- **Fetcher（请求层）**：负责HTTP请求、重试机制、User-Agent轮换
- **Parser（解析层）**：负责HTML解析、数据提取
- **Pipeline（存储层）**：负责数据清洗、验证、存储

## 🎯 核心功能

### 数据采集
- ✅ Steam畅销榜Top 100（支持指定日期）
- ✅ 自动提取AppID（从游戏链接）
- ✅ 完整价格信息（当前价、原价、折扣率）
- ✅ 多区域支持（当前实现US区）

### 爬虫特性
- ✅ User-Agent随机化（反检测）
- ✅ 指数退避重试机制（2s → 4s → 8s）
- ✅ 防御性编程（字段缺失不会崩溃）
- ✅ 完整日志记录（INFO/ERROR/CRITICAL）
- ✅ 数据质量验证

## 📦 安装依赖

```bash
pip install -r requirements.txt
```

## 🚀 快速开始

### 基础用法

```bash
python steam_crawler_v0.1.0.py
```

默认爬取**今日美国区**畅销榜，数据保存到 `data/raw/` 目录。

### 指定日期和区域

```python
from steam_crawler_v0.1.0 import SteamCrawler

crawler = SteamCrawler()
crawler.crawl(region="US", chart_date="2026-01-06")
```

## 📂 项目结构

```
爬虫代码开发/
├── steam_crawler_v0.1.0.py   # 主爬虫脚本
├── config.py                 # 配置文件（URL、选择器、重试等）
├── requirements.txt          # 依赖清单
├── README.md                 # 本文件
├── data/                     # 数据目录
│   └── raw/                  # 原始CSV文件
│       └── steam_topsellers_US_2026-01-06.csv
├── logs/                     # 日志目录
│   └── steam_crawler.log
└── docs/                     # 文档目录
    ├── CHANGELOG_V0.1.0.md   # 版本日志
    └── REFACTORING_PROPOSAL_V0.1.md  # 重构方案
```

## 📊 数据格式（CSV）

| 字段 | 说明 | 示例 |
|------|------|------|
| rank | 排名 | 1 |
| appid | Steam AppID | 1808500 |
| game_name | 游戏名称 | ARC Raiders |
| current_price | 当前价格 | 39.99 |
| original_price | 原价 | 39.99 |
| discount | 折扣率 | -30% |
| chart_date | 榜单日期 | 2026-01-06 |
| region | 区域 | US |
| crawl_time | 爬取时间 | 2026-01-06 10:30:00 |

## ⚙️ 配置说明

所有配置集中在 `config.py`，主要包括：

### URL配置
```python
CHARTS_URL_TEMPLATE = "https://store.steampowered.com/charts/topsellers/{region}/{date}"
```

### 重试配置
```python
RETRY_CONFIG = {
    "max_retries": 3,      # 最大重试次数
    "base_delay": 2,       # 基础延迟2秒
    "backoff_factor": 2,   # 指数增长因子
}
```

### CSS选择器
如果Steam页面结构变化，只需修改 `config.py` 中的 `SELECTORS` 字典。

## 🔍 日志说明

日志保存在 `logs/steam_crawler.log`，包含：

- **INFO**: 正常运行信息（请求成功、数据解析、保存完成）
- **WARNING**: 警告信息（数据量异常、AppID缺失）
- **ERROR**: 错误信息（请求失败、解析异常）
- **CRITICAL**: 严重错误（无法获取数据、程序崩溃）

## ⚠️ 注意事项

1. **请求频率**：默认请求间隔1秒，避免被Steam限流
2. **IP限制**：如遇403/429错误，建议：
   - 增加重试延迟
   - 使用代理（后续版本支持）
   - 降低爬取频率
3. **数据时效性**：榜单每日更新，建议每日定时爬取
4. **合法性**：仅供学习研究，请遵守Steam服务条款

## 🔜 后续版本计划

### V0.2.0（计划中）
- [ ] 支持多区域切换（CN/GLOBAL/EU）
- [ ] SQLite数据库存储
- [ ] 代理池支持
- [ ] 定时任务调度（cron/APScheduler）

### V0.3.0（计划中）
- [ ] 历史数据迁移工具
- [ ] 数据去重与增量更新
- [ ] Web可视化面板
- [ ] 异常监控与邮件告警

## 📝 开发日志

详见 `docs/CHANGELOG_V0.1.0.md`

## 👨‍💻 开发者

数据架构师 & 首席爬虫工程师

## 📄 许可证

本项目仅供学习研究使用，请勿用于商业用途。

