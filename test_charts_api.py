"""
测试脚本：探索Steam Charts数据获取方式
快速验证不同的数据获取方案
"""

import requests
import json
from datetime import datetime

# ==================== 方案1: 尝试可能的API端点 ====================
def test_possible_api_endpoints():
    """测试可能存在的Charts API端点"""
    
    # 可能的API端点列表
    potential_endpoints = [
        # 月度榜单可能的API
        "https://store.steampowered.com/charts/data/topnewreleases/december_2025",
        "https://store.steampowered.com/api/charts/topnewreleases/december_2025",
        "https://api.steampowered.com/IStoreService/GetCharts/v1/?month=december&year=2025",
        
        # 年度榜单可能的API
        "https://store.steampowered.com/charts/data/bestofyear/2025?tab=2",
        "https://store.steampowered.com/api/charts/bestofyear/2025",
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    }
    
    print("=" * 80)
    print("测试可能的API端点...")
    print("=" * 80)
    
    results = []
    
    for url in potential_endpoints:
        print(f"\n测试: {url}")
        try:
            response = requests.get(url, headers=headers, timeout=10)
            print(f"  状态码: {response.status_code}")
            
            if response.status_code == 200:
                print(f"  ✅ 成功! 内容类型: {response.headers.get('Content-Type')}")
                print(f"  内容长度: {len(response.text)} 字节")
                
                # 尝试解析JSON
                try:
                    data = response.json()
                    print(f"  📦 JSON数据: {json.dumps(data, indent=2, ensure_ascii=False)[:500]}...")
                    results.append({
                        "url": url,
                        "status": "success",
                        "data_type": "json",
                        "data": data
                    })
                except:
                    # 可能是HTML
                    print(f"  📄 HTML内容: {response.text[:200]}...")
                    results.append({
                        "url": url,
                        "status": "success",
                        "data_type": "html",
                        "content": response.text[:1000]
                    })
            else:
                print(f"  ❌ 失败: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ 错误: {str(e)}")
    
    return results


# ==================== 方案2: 请求页面并分析Network ====================
def get_page_and_show_info(url):
    """请求页面，查看返回内容"""
    
    print("\n" + "=" * 80)
    print(f"请求页面: {url}")
    print("=" * 80)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        print(f"状态码: {response.status_code}")
        print(f"内容类型: {response.headers.get('Content-Type')}")
        print(f"内容长度: {len(response.text)} 字节")
        
        # 检查是否包含React应用
        if 'react' in response.text.lower():
            print("✅ 检测到React应用 - 数据可能通过AJAX加载")
        
        # 检查是否有内联JSON数据
        if 'application/json' in response.text or '__INITIAL_STATE__' in response.text:
            print("✅ 可能包含内联JSON数据")
            
            # 尝试提取JSON
            import re
            json_pattern = r'<script[^>]*>.*?(\{.*?"appid".*?\}).*?</script>'
            matches = re.findall(json_pattern, response.text, re.DOTALL)
            if matches:
                print(f"找到 {len(matches)} 个可能的JSON数据块")
        
        return response.text
        
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        return None


# ==================== 主测试流程 ====================
if __name__ == "__main__":
    print("🚀 Steam Charts 数据获取方案测试")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 测试1: 尝试API端点
    print("\n\n【测试1】尝试可能的API端点")
    api_results = test_possible_api_endpoints()
    
    # 测试2: 请求实际页面
    print("\n\n【测试2】请求实际页面并分析")
    
    test_urls = [
        "https://store.steampowered.com/charts/topnewreleases/december_2025",
        "https://store.steampowered.com/charts/bestofyear/2025?tab=2",
    ]
    
    for url in test_urls:
        html_content = get_page_and_show_info(url)
        
        # 简单分析
        if html_content:
            if 'data-featuretarget="react-root"' in html_content:
                print("  📌 确认是React应用")
            
            # 查找可能的游戏数据
            import re
            appid_matches = re.findall(r'app/(\d+)', html_content)
            if appid_matches:
                unique_appids = list(set(appid_matches))[:10]
                print(f"  🎮 找到 {len(unique_appids)} 个游戏AppID示例: {unique_appids}")
    
    # 总结
    print("\n\n" + "=" * 80)
    print("📊 测试总结")
    print("=" * 80)
    
    if any(r.get('status') == 'success' and r.get('data_type') == 'json' for r in api_results):
        print("✅ 发现可用的JSON API端点 - 建议使用API方案")
    else:
        print("❌ 未发现直接可用的API端点")
        print("💡 建议方案:")
        print("   1. 使用DrissionPage爬取页面（React应用需要渲染）")
        print("   2. 或者手动抓包找到真实的数据接口")
    
    print("\n按回车键退出...")
    input()
