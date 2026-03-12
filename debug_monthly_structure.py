
from DrissionPage import ChromiumPage, ChromiumOptions
import time
import os

def debug_structure():
    print("Starting Debug...")
    
    co = ChromiumOptions()
    co.headless(False)
    page = ChromiumPage(co)
    
    url = "https://store.steampowered.com/charts/topnewreleases/april_2024"
    print(f"Visiting {url}")
    page.get(url)
    
    # 等待更长时间，确保加载
    time.sleep(10)
    
    # 滚动到底部触发懒加载
    print("Scrolling...")
    page.scroll.to_bottom()
    time.sleep(3)
    
    # 1. 检查等级标题
    print("\n[Check 1] Looking for Tier Headers...")
    # 尝试查找包含文本的元素
    tiers = ["Platinum", "Gold", "Silver", "Bronze", "铂金", "黄金", "白银", "青铜"]
    for tier in tiers:
        eles = page.eles(f'xpath://div[contains(text(), "{tier}")]')
        if eles:
            print(f"Found '{tier}': {len(eles)} elements")
            for i, ele in enumerate(eles[:3]):
                print(f"  - Ele {i}: Tag={ele.tag}, Class={ele.attr('class')}, Text='{ele.text[:30]}...'")
        else:
            print(f"Not found: '{tier}'")

    # 2. 检查游戏卡片和名称
    print("\n[Check 2] Looking for Game Names...")
    # 尝试查找通用的游戏名类名
    name_classes = ["StoreSaleWidgetTitle", "items_GameName", "AppName"]
    for cls in name_classes:
        eles = page.eles(f'css:div[class*="{cls}"]')
        if eles:
            print(f"Found class '*{cls}*': {len(eles)} elements")
            for i, ele in enumerate(eles[:3]):
                print(f"  - Name: {ele.text}")
        else:
            print(f"Not found class: '*{cls}*'")
            
    # 3. 保存HTML
    filename = "debug_monthly_page.html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(page.html)
    print(f"\nSaved full HTML to {os.path.abspath(filename)}")
    
    page.quit()

if __name__ == "__main__":
    debug_structure()
