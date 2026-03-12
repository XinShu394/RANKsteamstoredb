"""
快速测试脚本 - 自动获取2025年12月和2025年度榜单
"""

import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(__file__))

from steam_charts_crawler import MonthlyNewReleasesCrawler, YearlyBestCrawler, logger
import config_charts as config


def test_monthly_2025_12():
    """测试2025年12月的月度新品榜单"""
    print("\n" + "=" * 70)
    print("[测试 1] 获取2025年12月月度新品榜单")
    print("=" * 70 + "\n")
    
    try:
        crawler = MonthlyNewReleasesCrawler()
        if not crawler.init_browser():
            print("\n[失败] 浏览器初始化失败")
            return False
        
        df = crawler.crawl(month="12", year=2025)
        
        if df is not None and not df.empty:
            result = {
                'success': True,
                'total_games': len(df),
                'data': df.to_dict('records'),
                'csv_file': 'steam_monthly_december_2025.csv',
                'excel_file': 'steam_monthly_december_2025.xlsx'
            }
        else:
            result = {'success': False, 'error': '未获取到数据'}
        
        if result['success']:
            print(f"\n[成功] 获取了 {result['total_games']} 款游戏")
            print(f"CSV文件: {result['csv_file']}")
            print(f"Excel文件: {result['excel_file']}")
            
            # 显示前5款游戏
            if result['data']:
                print("\n前5款游戏：")
                for i, game in enumerate(result['data'][:5], 1):
                    print(f"   {i}. {game.get('游戏名称', 'N/A')}")
        else:
            print(f"\n[失败] {result.get('error', '未知错误')}")
        
        return result['success']
    
    except Exception as e:
        print(f"\n[错误] {str(e)}")
        logger.error(f"测试月度榜单失败: {str(e)}")
        return False


def test_yearly_2025_tab1():
    """测试2025年度榜单 - Tab 1 (年度最畅销)"""
    print("\n" + "=" * 70)
    print("[测试 2] 获取2025年度最畅销榜单")
    print("=" * 70 + "\n")
    
    try:
        crawler = YearlyBestCrawler()
        if not crawler.init_browser():
            print("\n[失败] 浏览器初始化失败")
            return False
        
        df = crawler.crawl(year=2025, tab=1)
        
        if df is not None and not df.empty:
            result = {
                'success': True,
                'total_games': len(df),
                'data': df.to_dict('records'),
                'csv_file': 'steam_yearly_2025_tab1_top_sellers.csv',
                'excel_file': 'steam_yearly_2025_tab1_top_sellers.xlsx'
            }
        else:
            result = {'success': False, 'error': '未获取到数据'}
        
        if result['success']:
            print(f"\n[成功] 获取了 {result['total_games']} 款游戏")
            print(f"CSV文件: {result['csv_file']}")
            print(f"Excel文件: {result['excel_file']}")
            
            # 显示前5款游戏
            if result['data']:
                print("\n前5款游戏：")
                for i, game in enumerate(result['data'][:5], 1):
                    print(f"   {i}. {game.get('游戏名称', 'N/A')}")
        else:
            print(f"\n[失败] {result.get('error', '未知错误')}")
        
        return result['success']
    
    except Exception as e:
        print(f"\n[错误] {str(e)}")
        logger.error(f"测试年度榜单失败: {str(e)}")
        return False


def main():
    """主函数"""
    print("\n" + "=" * 70)
    print("           Steam 2025年榜单数据测试")
    print("=" * 70)
    print("\n将自动测试以下两个榜单：")
    print("  [1]  2025年12月月度新品榜单")
    print("  [2]  2025年度最畅销榜单")
    print("\n预计耗时: 2-3分钟")
    print("=" * 70 + "\n")
    
    print("开始测试...\n")
    
    # 测试1: 月度榜单
    success1 = test_monthly_2025_12()
    
    # 测试2: 年度榜单
    success2 = test_yearly_2025_tab1()
    
    # 总结
    print("\n" + "=" * 70)
    print("测试总结")
    print("=" * 70)
    print(f"  * 2025年12月月度榜单: {'[成功]' if success1 else '[失败]'}")
    print(f"  * 2025年度最畅销榜单: {'[成功]' if success2 else '[失败]'}")
    print("=" * 70 + "\n")
    
    if success1 and success2:
        print("[完成] 所有测试通过！数据文件已保存到 data/charts/raw/ 目录")
    else:
        print("[警告] 部分测试失败，请查看日志文件了解详情")
        print("日志文件: logs/steam_charts_crawler.log")
    
    print("\n测试完成！\n")


if __name__ == "__main__":
    main()
