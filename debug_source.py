"""
调试脚本：检查 YearlyBestCrawler 的源代码
"""
import sys
import os
import inspect

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(__file__))

from steam_charts_crawler import YearlyBestCrawler

print("=" * 80)
print("检查 YearlyBestCrawler._extract_game_data 源代码")
print("=" * 80)

try:
    source = inspect.getsource(YearlyBestCrawler._extract_game_data)
    print(source)
except Exception as e:
    print(f"无法获取源代码: {e}")

print("=" * 80)
