"""
Steam Charts 榜单爬虫 - 交互式启动脚本
提供友好的用户交互界面
"""

import sys
from datetime import datetime
from steam_charts_crawler import MonthlyNewReleasesCrawler, YearlyBestCrawler, logger
import config_charts as config


def print_header():
    """打印标题"""
    print("\n" + "=" * 70)
    print("           Steam Charts 榜单爬虫 V1.0.0")
    print("=" * 70)
    print("\n📊 本工具可以爬取：")
    print("  1️⃣  月度新品榜单 (Top New Releases)")
    print("  2️⃣  年度榜单 (Best of Year)")
    print("\n✨ 数据将保存为 CSV 和 Excel 格式")
    print("=" * 70 + "\n")


def get_user_choice():
    """获取用户选择"""
    while True:
        print("请选择要爬取的榜单类型：")
        print("  [1] 月度新品榜单")
        print("  [2] 年度榜单（单个tab）")
        print("  [3] 年度榜单（全部6个tab）")
        print("  [0] 退出")
        
        choice = input("\n请输入选项 (0-3): ").strip()
        
        if choice in ['0', '1', '2', '3']:
            return choice
        else:
            print("❌ 无效选项，请重新输入！\n")


def crawl_monthly():
    """爬取月度榜单"""
    print("\n" + "=" * 70)
    print("📅 月度新品榜单爬取")
    print("=" * 70)
    
    # 获取年份
    current_year = datetime.now().year
    while True:
        year_input = input(f"\n请输入年份 (例如: {current_year}, 直接回车使用{current_year}): ").strip()
        if not year_input:
            year = current_year
            break
        
        try:
            year = int(year_input)
            if 2020 <= year <= 2030:
                break
            else:
                print("❌ 年份应在 2020-2030 之间")
        except ValueError:
            print("❌ 请输入有效的年份数字")
    
    # 获取月份
    print("\n请输入月份：")
    print("  - 数字: 1-12")
    print("  - 或英文: january, february, ..., december")
    
    current_month = datetime.now().month
    while True:
        month_input = input(f"\n请输入月份 (直接回车使用当前月份 {current_month}): ").strip()
        if not month_input:
            month = str(current_month)
            break
        
        # 验证月份
        if month_input.isdigit() and 1 <= int(month_input) <= 12:
            month = month_input
            break
        elif month_input.lower() in [v for v in config.MONTH_MAP.values()]:
            month = month_input.lower()
            break
        else:
            print("❌ 无效的月份，请重新输入")
    
    # 确认
    month_name = config.MONTH_MAP.get(month, month)
    print(f"\n✅ 将爬取: {year}年 {month_name} 月度新品榜单")
    confirm = input("确认开始？(Y/n): ").strip().lower()
    
    if confirm == 'n':
        print("❌ 已取消")
        return
    
    # 开始爬取
    print("\n🚀 开始爬取...\n")
    crawler = MonthlyNewReleasesCrawler()
    df = crawler.crawl(month, year)
    
    if df is not None and len(df) > 0:
        print("\n" + "=" * 70)
        print("✅ 爬取成功！")
        print("=" * 70)
        print(f"📊 共获取 {len(df)} 个游戏")
        print(f"💾 数据已保存到: {config.OUTPUT_CONFIG['output_dir']}")
        print("\n前5个游戏预览：")
        print(df.head().to_string(index=False))
    else:
        print("\n❌ 爬取失败，请查看日志文件获取详细信息")


def crawl_yearly_single():
    """爬取年度榜单（单个tab）"""
    print("\n" + "=" * 70)
    print("🏆 年度榜单爬取（单个tab）")
    print("=" * 70)
    
    # 获取年份
    current_year = datetime.now().year
    while True:
        year_input = input(f"\n请输入年份 (例如: {current_year}, 直接回车使用{current_year}): ").strip()
        if not year_input:
            year = current_year
            break
        
        try:
            year = int(year_input)
            if 2020 <= year <= 2030:
                break
            else:
                print("❌ 年份应在 2020-2030 之间")
        except ValueError:
            print("❌ 请输入有效的年份数字")
    
    # 显示tab选项
    print("\n请选择榜单类型（Tab）：")
    for tab_id, tab_name in config.YEARLY_TAB_MAP.items():
        print(f"  [{tab_id}] {tab_name}")
    
    while True:
        tab_input = input("\n请输入Tab编号 (0-5): ").strip()
        if tab_input in config.YEARLY_TAB_MAP:
            tab = int(tab_input)
            break
        else:
            print("❌ 无效的Tab编号")
    
    # 确认
    tab_name = config.YEARLY_TAB_MAP[str(tab)]
    print(f"\n✅ 将爬取: {year}年度 - {tab_name}")
    confirm = input("确认开始？(Y/n): ").strip().lower()
    
    if confirm == 'n':
        print("❌ 已取消")
        return
    
    # 开始爬取
    print("\n🚀 开始爬取...\n")
    crawler = YearlyBestCrawler()
    df = crawler.crawl(year, tab)
    
    if df is not None and len(df) > 0:
        print("\n" + "=" * 70)
        print("✅ 爬取成功！")
        print("=" * 70)
        print(f"📊 共获取 {len(df)} 个游戏")
        print(f"💾 数据已保存到: {config.OUTPUT_CONFIG['output_dir']}")
        print("\n前5个游戏预览：")
        print(df.head().to_string(index=False))
    else:
        print("\n❌ 爬取失败，请查看日志文件获取详细信息")


def crawl_yearly_all():
    """爬取年度榜单（全部tab）"""
    print("\n" + "=" * 70)
    print("🏆 年度榜单爬取（全部6个tab）")
    print("=" * 70)
    
    # 获取年份
    current_year = datetime.now().year
    while True:
        year_input = input(f"\n请输入年份 (例如: {current_year}, 直接回车使用{current_year}): ").strip()
        if not year_input:
            year = current_year
            break
        
        try:
            year = int(year_input)
            if 2020 <= year <= 2030:
                break
            else:
                print("❌ 年份应在 2020-2030 之间")
        except ValueError:
            print("❌ 请输入有效的年份数字")
    
    # 确认
    print(f"\n✅ 将爬取 {year}年度 的全部6个榜单：")
    for tab_id, tab_name in config.YEARLY_TAB_MAP.items():
        print(f"  • {tab_name}")
    
    print("\n⚠️ 这将花费较长时间（约3-5分钟）")
    confirm = input("确认开始？(Y/n): ").strip().lower()
    
    if confirm == 'n':
        print("❌ 已取消")
        return
    
    # 开始爬取
    print("\n🚀 开始爬取...\n")
    crawler = YearlyBestCrawler()
    results = crawler.crawl_all_tabs(year)
    
    # 显示结果
    print("\n" + "=" * 70)
    print("📊 爬取完成！统计结果：")
    print("=" * 70)
    
    total_games = 0
    for tab, df in results.items():
        tab_name = config.YEARLY_TAB_MAP[str(tab)]
        game_count = len(df) if df is not None else 0
        total_games += game_count
        status = "✅" if game_count > 0 else "❌"
        print(f"{status} Tab {tab} - {tab_name}: {game_count} 个游戏")
    
    print(f"\n📈 总计: {total_games} 个游戏记录")
    print(f"💾 数据已保存到: {config.OUTPUT_CONFIG['output_dir']}")


def main():
    """主函数"""
    print_header()
    
    while True:
        choice = get_user_choice()
        
        if choice == '0':
            print("\n👋 再见！")
            break
        elif choice == '1':
            crawl_monthly()
        elif choice == '2':
            crawl_yearly_single()
        elif choice == '3':
            crawl_yearly_all()
        
        # 询问是否继续
        print("\n" + "=" * 70)
        continue_choice = input("\n是否继续爬取其他榜单？(Y/n): ").strip().lower()
        if continue_choice == 'n':
            print("\n👋 再见！")
            break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断")
        sys.exit(0)
    except Exception as e:
        logger.error(f"程序异常: {str(e)}", exc_info=True)
        print(f"\n❌ 程序出错: {str(e)}")
        input("\n按回车键退出...")
        sys.exit(1)
