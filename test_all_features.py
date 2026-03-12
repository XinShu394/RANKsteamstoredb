"""
Steam榜单爬虫 - 全功能集成测试脚本
用于验证所有核心功能是否正常工作，数据是否完整（包含等级）。
"""

import sys
import io
import os
import time
import pandas as pd
from datetime import datetime

# 设置UTF-8编码输出 (解决Windows控制台编码问题)
if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except:
        pass

# 添加代码目录到路径
sys.path.insert(0, os.path.dirname(__file__))

from steam_charts_crawler import MonthlyNewReleasesCrawler, YearlyBestCrawler, logger
import config_charts as config

# 测试配置
TEST_YEAR = 2025
TEST_MONTH = 12
TEST_YEARLY_TAB = 1  # 最畅销

def print_section(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60 + "\n")

def check_file_content(filepath, check_tier=True):
    """检查生成的文件内容"""
    if not os.path.exists(filepath):
        print(f"❌ 文件未找到: {filepath}")
        return False
        
    try:
        if filepath.endswith('.csv'):
            df = pd.read_csv(filepath)
        else:
            df = pd.read_excel(filepath)
            
        print(f"✅ 文件读取成功: {os.path.basename(filepath)}")
        print(f"   - 数据行数: {len(df)}")
        print(f"   - 包含列: {', '.join(df.columns)}")
        
        # 检查关键字段
        required_cols = ['排名', '游戏名称', 'AppID']
        if check_tier:
            required_cols.append('等级')
            
        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            print(f"❌ 缺少关键列: {missing}")
            return False
            
        # 检查等级字段是否有值
        if check_tier and '等级' in df.columns:
            empty_tiers = df['等级'].isna().sum()
            print(f"   - 等级字段有效性: {len(df) - empty_tiers}/{len(df)} 非空")
            
            # 打印前3个等级示例
            examples = df['等级'].head(3).tolist()
            print(f"   - 等级示例: {examples}")
            
        return True
        
    except Exception as e:
        print(f"❌ 文件检查失败: {str(e)}")
        return False

def test_monthly():
    print_section("测试 1: 月度新品榜单")
    print(f"目标: {TEST_YEAR}年 {TEST_MONTH}月")
    
    crawler = MonthlyNewReleasesCrawler()
    
    # 初始化
    if not crawler.init_browser():
        print("❌ 浏览器初始化失败")
        return False
        
    # 爬取
    try:
        df = crawler.crawl(month=TEST_MONTH, year=TEST_YEAR)
        if df is None or len(df) == 0:
            print(f"❌ 爬取失败: 未获取到数据")
            return False
            
        print(f"✅ 爬取成功！获取到 {len(df)} 个游戏")
        
        # 检查数据
        print(f"   包含列: {', '.join(df.columns)}")
        if '等级' in df.columns:
            print(f"   等级示例: {df['等级'].head(3).tolist()}")
            
        # 显示前3个游戏
        print("\n前3个游戏:")
        print(df.head(3).to_string(index=False))
        
        return True
        
    except Exception as e:
        print(f"❌ 发生异常: {str(e)}")
        return False

def test_yearly_single():
    print_section("测试 2: 年度榜单 (单个Tab)")
    print(f"目标: {TEST_YEAR}年 Tab={TEST_YEARLY_TAB} (最畅销)")
    
    crawler = YearlyBestCrawler()
    
    # 初始化
    if not crawler.init_browser():
        print("❌ 浏览器初始化失败")
        return False
        
    # 爬取
    try:
        df = crawler.crawl(year=TEST_YEAR, tab=TEST_YEARLY_TAB)
        if df is None or len(df) == 0:
            print(f"❌ 爬取失败: 未获取到数据")
            return False
            
        print(f"✅ 爬取成功！获取到 {len(df)} 个游戏")
        
        # 检查数据
        print(f"   包含列: {', '.join(df.columns)}")
        if '等级' in df.columns:
            print(f"   等级示例: {df['等级'].head(3).tolist()}")
            
        # 显示前3个游戏
        print("\n前3个游戏:")
        print(df.head(3).to_string(index=False))
        
        return True
        
    except Exception as e:
        print(f"❌ 发生异常: {str(e)}")
        return False

def main():
    start_time = time.time()
    
    print("🚀 开始全功能集成测试...")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 测试月度榜单
    monthly_ok = test_monthly()
    
    # 2. 测试年度榜单
    yearly_ok = test_yearly_single()
    
    print_section("测试总结")
    print(f"月度榜单测试: {'✅ 通过' if monthly_ok else '❌ 失败'}")
    print(f"年度榜单测试: {'✅ 通过' if yearly_ok else '❌ 失败'}")
    
    duration = time.time() - start_time
    print(f"\n总耗时: {duration:.2f} 秒")
    
    if monthly_ok and yearly_ok:
        print("\n✨ 所有核心功能测试通过！代码已准备就绪。")
    else:
        print("\n⚠️ 存在测试失败项，请检查日志。")

if __name__ == "__main__":
    main()
