"""
Steam榜单结构分析脚本
用于分析页面HTML结构，特别是寻找"等级"（Platinum, Gold等）相关的元素
"""
import sys
import os
import time
from DrissionPage import ChromiumPage, ChromiumOptions

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(__file__))
import config_charts as config

def inspect_page():
    print("启动浏览器进行结构分析...")
    
    co = ChromiumOptions()
    co.headless(False)  # 有头模式可以看到
    page = ChromiumPage(co)
    
    # 1. 分析年度榜单 (2025 Tab 1)
    url = "https://store.steampowered.com/charts/bestofyear/2025?tab=1"
    print(f"\n正在访问: {url}")
    page.get(url)
    time.sleep(5)
    
    print("\n[分析年度榜单结构]")
    
    # 查找可能的等级关键词
    keywords = ["Platinum", "Gold", "Silver", "Bronze", "铂金", "黄金", "白银", "青铜"]
    
    found_tiers = False
    for kw in keywords:
        # 查找包含关键词的元素
        # 使用xpath查找包含文本的元素
        eles = page.eles(f'xpath://*[contains(text(), "{kw}")]')
        if eles:
            print(f"\n找到关键词 '{kw}': {len(eles)} 个元素")
            for i, ele in enumerate(eles[:3]):
                print(f"  元素 {i+1}: Tag={ele.tag}, Class={ele.attr('class')}")
                # 打印父级结构，看看是不是容器标题
                parent = ele.parent()
                print(f"  父级: Tag={parent.tag}, Class={parent.attr('class')}")
                found_tiers = True
    
    if not found_tiers:
        print("\n未找到明显的文本关键词。尝试查找可能的容器类名...")
        
        # 查找包含大量游戏链接的容器
        # 通常游戏链接包含 /app/
        links = page.eles('css:a[href*="/app/"]')
        if links:
            print(f"找到 {len(links)} 个游戏链接")
            first_link = links[0]
            
            # 向上查找父级，看看哪一级是分组容器
            curr = first_link
            for i in range(5):
                curr = curr.parent()
                print(f"  Level {i+1} Parent: Tag={curr.tag}, Class={curr.attr('class')}")
                # 检查这个父级是否有兄弟节点（可能是其他等级的容器）
                siblings = curr.next_siblings()
                if siblings:
                    print(f"    兄弟节点数: {len(siblings)}")
    
    # 2. 分析月度榜单 (2025 12月)
    url_monthly = "https://store.steampowered.com/charts/topnewreleases/december_2025"
    print(f"\n正在访问: {url_monthly}")
    page.get(url_monthly)
    time.sleep(5)
    
    print("\n[分析月度榜单结构]")
    # 同样查找关键词
    for kw in ["Top", "New", "Release", "Popular", "最热", "新品"]:
         eles = page.eles(f'xpath://*[contains(text(), "{kw}")]')
         if eles:
             # 过滤掉导航栏等无关元素，只看可能是标题的
             relevant = [e for e in eles if e.tag in ['div', 'h1', 'h2', 'h3', 'span']]
             if relevant:
                 print(f"关键词 '{kw}': {len(relevant)} 个相关元素")
                 for e in relevant[:2]:
                     print(f"  Tag={e.tag}, Class={e.attr('class')}, Text={e.text[:50]}")

    page.quit()

if __name__ == "__main__":
    inspect_page()
