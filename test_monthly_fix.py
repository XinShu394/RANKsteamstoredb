
from DrissionPage import ChromiumPage, ChromiumOptions
from steam_charts_crawler import MonthlyNewReleasesCrawler, setup_logging
import pandas as pd
import os

# 配置日志 - 打印到控制台
setup_logging()

def test_fix():
    print("Starting Monthly Fix Test (April 2024)...")
    
    co = ChromiumOptions()
    co.headless(False)
    page = ChromiumPage(co)
    
    crawler = MonthlyNewReleasesCrawler(page=page)
    
    # 强制在当前目录生成一个测试文件，方便查找
    output_file = "test_result_april_2024.csv"
    if os.path.exists(output_file):
        os.remove(output_file)
        
    print("Crawling...")
    # 测试 2024年4月
    df = crawler.crawl(month="4", year=2024)
    
    if df is not None:
        print(f"\n[SUCCESS] Got {len(df)} rows")
        
        # 保存到当前目录
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"Saved test file to: {os.path.abspath(output_file)}")

        print("\nData Preview (Top 10):")
        print(df[["排名", "等级", "游戏名称", "AppID"]].head(10).to_string())
        
        # 检查是否有不同的等级
        tiers = df["等级"].unique()
        print(f"\nDetected Tiers: {tiers}")
    else:
        print("[FAIL] Crawl returned None")
        
    page.quit()

if __name__ == "__main__":
    test_fix()
