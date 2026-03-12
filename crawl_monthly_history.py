"""
月榜批量爬取脚本
功能：自动爬取从 2020年1月 至今的所有月度新品榜单
"""

import time
import datetime
from DrissionPage import ChromiumPage, ChromiumOptions
import config_charts as config
from steam_charts_crawler import MonthlyNewReleasesCrawler, setup_logging

# 设置日志
logger = setup_logging()

def main():
    # 1. 动态修改输出目录为批量目录
    config.OUTPUT_CONFIG["output_dir"] = config.BATCH_CONFIG["monthly_output_dir"]
    logger.info(f"📂 输出目录已设置为: {config.OUTPUT_CONFIG['output_dir']}")
    
    # 2. 初始化共享浏览器
    co = ChromiumOptions()
    co.headless(False)
    page = ChromiumPage(co)
    
    crawler = MonthlyNewReleasesCrawler(page=page)
    
    # 3. 计算时间范围
    start_year = config.BATCH_CONFIG["monthly_start_year"]
    start_month = config.BATCH_CONFIG["monthly_start_month"]
    
    now = datetime.datetime.now()
    current_year = now.year
    current_month = now.month
    
    logger.info(f"🚀 开始批量爬取任务: {start_year}-{start_month} 至 {current_year}-{current_month}")
    
    total_months = 0
    success_count = 0
    
    try:
        for year in range(start_year, current_year + 1):
            # 确定该年的起始月份和结束月份
            month_start = start_month if year == start_year else 1
            month_end = current_month if year == current_year else 12
            
            for month in range(month_start, month_end + 1):
                total_months += 1
                month_str = str(month)
                
                logger.info(f"\n[{total_months}] 正在处理: {year}年 {month}月")
                
                # 执行爬取
                df = crawler.crawl(month=month_str, year=year)
                
                if df is not None and not df.empty:
                    success_count += 1
                    logger.info(f"✅ {year}年{month}月爬取成功，共 {len(df)} 条数据")
                else:
                    logger.error(f"❌ {year}年{month}月爬取失败或无数据")
                
                # 随机延时，避免请求过快
                time.sleep(2)
                
    except KeyboardInterrupt:
        logger.warning("\n⚠️ 用户中断任务")
    except Exception as e:
        logger.error(f"\n❌ 发生严重错误: {str(e)}", exc_info=True)
    finally:
        # 关闭浏览器
        if page:
            page.quit()
        
        logger.info(f"\n{'='*50}")
        logger.info(f"🎉 批量任务结束")
        logger.info(f"📊 总计尝试: {total_months} 个月")
        logger.info(f"✅ 成功: {success_count} 个")
        logger.info(f"📂 数据保存在: {config.OUTPUT_CONFIG['output_dir']}")
        logger.info(f"{'='*50}")

if __name__ == "__main__":
    main()
