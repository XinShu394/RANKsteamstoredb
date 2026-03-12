"""
快速测试脚本 - Steam Charts 爬虫
用于验证爬虫基本功能
"""

import sys
import io
from datetime import datetime
from steam_charts_crawler import MonthlyNewReleasesCrawler, YearlyBestCrawler, logger

# 设置UTF-8编码输出 (解决Windows控制台编码问题)
if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except:
        pass


def test_monthly():
    """测试月度榜单爬取"""
    print("\n" + "=" * 70)
    print("【测试1】月度新品榜单")
    print("=" * 70)
    
    # 测试 2025年12月
    crawler = MonthlyNewReleasesCrawler()
    df = crawler.crawl("12", 2025)
    
    if df is not None and len(df) > 0:
        print("\n✅ 月度榜单测试成功！")
        print(f"📊 获取到 {len(df)} 个游戏")
        print("\n前3个游戏：")
        print(df.head(3).to_string(index=False))
        return True
    else:
        print("\n❌ 月度榜单测试失败")
        return False


def test_yearly():
    """测试年度榜单爬取"""
    print("\n" + "=" * 70)
    print("【测试2】年度榜单（Tab 2 - 最多游玩）")
    print("=" * 70)
    
    # 测试 2025年 Tab 2
    crawler = YearlyBestCrawler()
    df = crawler.crawl(2025, 2)
    
    if df is not None and len(df) > 0:
        print("\n✅ 年度榜单测试成功！")
        print(f"📊 获取到 {len(df)} 个游戏")
        print("\n前3个游戏：")
        print(df.head(3).to_string(index=False))
        return True
    else:
        print("\n❌ 年度榜单测试失败")
        return False


def main():
    """主测试流程"""
    print("=" * 70)
    print("         Steam Charts 爬虫 - 快速测试")
    print("=" * 70)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {}
    
    # 测试1: 月度榜单
    try:
        results['monthly'] = test_monthly()
    except Exception as e:
        print(f"\n❌ 月度榜单测试异常: {str(e)}")
        results['monthly'] = False
    
    # 间隔等待
    print("\n⏳ 等待3秒后继续下一个测试...")
    import time
    time.sleep(3)
    
    # 测试2: 年度榜单
    try:
        results['yearly'] = test_yearly()
    except Exception as e:
        print(f"\n❌ 年度榜单测试异常: {str(e)}")
        results['yearly'] = False
    
    # 总结
    print("\n" + "=" * 70)
    print("📊 测试总结")
    print("=" * 70)
    
    passed = sum(results.values())
    total = len(results)
    
    print(f"✅ 通过: {passed}/{total}")
    print(f"❌ 失败: {total - passed}/{total}")
    
    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
    
    if passed == total:
        print("\n🎉 所有测试通过！")
    else:
        print("\n⚠️ 部分测试失败，请查看日志文件")
        print(f"日志位置: logs/steam_charts_crawler.log")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ 测试被中断")
        sys.exit(0)
    except Exception as e:
        logger.error(f"测试异常: {str(e)}", exc_info=True)
        print(f"\n❌ 测试出错: {str(e)}")
    finally:
        input("\n按回车键退出...")
