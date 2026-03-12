# Steam Charts 榜单爬虫 V1.0.0

## 📖 简介

这是一个**独立**的Steam榜单爬虫工具，专门用于爬取：
- 📅 **月度新品榜单** (Top New Releases)
- 🏆 **年度榜单** (Best of Year - 6个不同类别)

**重要说明**：
- ✅ 完全独立，不影响原有的畅销榜爬虫功能
- ✅ 独立的配置文件、数据目录、日志文件
- ✅ 用户友好的交互界面

---

## 📂 文件结构

```
爬虫代码开发steam/code/
├── config_charts.py              # Charts爬虫配置（独立）
├── steam_charts_crawler.py       # 核心爬虫代码
├── run_charts_crawler.py         # 交互式启动脚本
├── run_charts_crawler.bat        # Windows批处理启动
│
├── data/
│   └── charts/                   # Charts数据目录（独立）
│       └── raw/                  # 存放CSV和Excel文件
│
└── logs/
    └── steam_charts_crawler.log  # Charts爬虫日志（独立）
```

---

## 🚀 快速开始

### 方式1：双击运行（推荐）

1. 双击 `run_charts_crawler.bat`
2. 按照提示选择榜单类型
3. 输入年份、月份等信息
4. 等待爬取完成

### 方式2：命令行运行

```bash
cd 爬虫代码开发steam/code
python run_charts_crawler.py
```

---

## 📊 功能说明

### 1. 月度新品榜单

**URL示例**：
- https://store.steampowered.com/charts/topnewreleases/december_2025
- https://store.steampowered.com/charts/topnewreleases/january_2026

**使用步骤**：
1. 选择选项 `[1] 月度新品榜单`
2. 输入年份（如 `2025`）
3. 输入月份（如 `12` 或 `december`）
4. 确认并开始爬取

**输出文件**：
- `steam_monthly_december_2025.csv`
- `steam_monthly_december_2025.xlsx`

---

### 2. 年度榜单（单个tab）

**URL示例**：
- https://store.steampowered.com/charts/bestofyear/2025?tab=0
- https://store.steampowered.com/charts/bestofyear/2025?tab=2

**Tab类型**：
- `Tab 0`: 年度最佳游戏
- `Tab 1`: 年度最畅销
- `Tab 2`: 年度最多游玩
- `Tab 3`: 年度最受好评
- `Tab 4`: 年度新晋佳作
- `Tab 5`: 年度最佳抢先体验

**使用步骤**：
1. 选择选项 `[2] 年度榜单（单个tab）`
2. 输入年份（如 `2025`）
3. 选择Tab编号（0-5）
4. 确认并开始爬取

**输出文件**：
- `steam_yearly_2025_tab2_most_played.csv`
- `steam_yearly_2025_tab2_most_played.xlsx`

---

### 3. 年度榜单（全部6个tab）

**使用步骤**：
1. 选择选项 `[3] 年度榜单（全部6个tab）`
2. 输入年份（如 `2025`）
3. 确认并开始爬取（约3-5分钟）

**输出文件**（6个）：
- `steam_yearly_2025_tab0_best_of_year.xlsx`
- `steam_yearly_2025_tab1_top_sellers.xlsx`
- `steam_yearly_2025_tab2_most_played.xlsx`
- `steam_yearly_2025_tab3_best_rated.xlsx`
- `steam_yearly_2025_tab4_best_new_release.xlsx`
- `steam_yearly_2025_tab5_best_early_access.xlsx`

---

## 📁 输出数据格式

### CSV/Excel 文件结构

| 排名 | 游戏名称 | AppID | 链接 |
|------|----------|-------|------|
| 1 | 游戏A | 123456 | https://store.steampowered.com/app/123456 |
| 2 | 游戏B | 789012 | https://store.steampowered.com/app/789012 |
| ... | ... | ... | ... |

---

## ⚙️ 配置说明

### 修改配置

编辑 `config_charts.py` 文件：

```python
# 页面加载等待时间
PAGE_LOAD_CONFIG = {
    "wait_time": 5,           # React加载等待（秒）
    "scroll_wait": 1,         # 滚动等待（秒）
    "max_scroll_times": 3,    # 最大滚动次数
}

# 调试配置
DEBUG_CONFIG = {
    "save_html": True,        # 保存HTML快照
    "save_screenshot": True,  # 保存截图
}
```

---

## 🔍 日志查看

**日志文件位置**：`logs/steam_charts_crawler.log`

**查看方式**：
```bash
# Windows
type logs\steam_charts_crawler.log

# 或用文本编辑器打开
notepad logs\steam_charts_crawler.log
```

---

## ❓ 常见问题

### Q1: 爬取到的游戏数量很少？

**原因**：页面可能需要更长的加载时间

**解决**：
1. 编辑 `config_charts.py`
2. 增加 `wait_time` 的值（如改为 8-10秒）

### Q2: 浏览器闪退？

**原因**：DrissionPage或Chrome路径问题

**解决**：
1. 检查Chrome浏览器是否已安装
2. 更新DrissionPage：`pip install --upgrade DrissionPage`

### Q3: 提取不到游戏名称？

**原因**：Steam页面结构可能变化

**解决**：
1. 查看保存的HTML文件（在 `logs/` 目录）
2. 分析页面结构
3. 调整 `_parse_page()` 方法中的解析逻辑

### Q4: 会影响原有的畅销榜爬虫吗？

**答案**：不会！

**原因**：
- 独立的配置文件（`config_charts.py` vs `config.py`）
- 独立的日志文件（`steam_charts_crawler.log` vs `steam_crawler.log`）
- 独立的数据目录（`data/charts/` vs `data/raw/`）

---

## 🛠️ 依赖要求

### Python版本
- Python 3.8 或更高

### 依赖包
```bash
pip install DrissionPage pandas openpyxl
```

或使用原有的 `requirements.txt`：
```bash
pip install -r requirements.txt
```

---

## 📝 更新日志

### V1.0.0 (2026-01-21)
- ✅ 初始版本
- ✅ 支持月度新品榜单爬取
- ✅ 支持年度榜单爬取（6个tab）
- ✅ 提供交互式用户界面
- ✅ 独立的配置和数据管理

---

## 🤝 与原有爬虫的关系

| 特性 | 原有畅销榜爬虫 | Charts榜单爬虫 |
|------|----------------|----------------|
| 配置文件 | `config.py` | `config_charts.py` |
| 主程序 | `steam_crawler_v0.3.0.py` | `steam_charts_crawler.py` |
| 启动脚本 | `run_crawler_v3_interactive.bat` | `run_charts_crawler.bat` |
| 数据目录 | `data/raw/` | `data/charts/raw/` |
| 日志文件 | `steam_crawler.log` | `steam_charts_crawler.log` |
| 功能 | 畅销榜（按地区/日期） | 月度/年度榜单 |

**结论**：两者完全独立，互不影响！

---

## 📧 技术支持

如有问题，请查看：
1. 日志文件：`logs/steam_charts_crawler.log`
2. 调试HTML：`logs/debug_*.html`
3. 原有文档：`docs/` 目录

---

## 📜 许可证

与原项目保持一致

---

**祝你使用愉快！🎉**
