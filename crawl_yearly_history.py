"""
年榜批量爬取脚本
功能：自动爬取从 2017年 至今的所有年度榜单 (包含所有类别)
"""

import time
import datetime
from DrissionPage import ChromiumPage, ChromiumOptions
import config_charts as config
from steam_charts_crawler import YearlyBestCrawler, setup_logging

# 设置日志
logger = setup_logging()

def main():
    # 1. 动态修改输出目录为批量目录
    config.OUTPUT_CONFIG["output_dir"] = config.BATCH_CONFIG["yearly_output_dir"]
    logger.info(f"📂 输出目录已设置为: {config.OUTPUT_CONFIG['output_dir']}")
    
    # 2. 初始化共享浏览器
    co = ChromiumOptions()
    co.headless(False)
    page = ChromiumPage(co)
    
    crawler = YearlyBestCrawler(page=page)
    
    # 3. 计算时间范围
    start_year = config.BATCH_CONFIG["yearly_start_year"]
    
    now = datetime.datetime.now()
    current_year = now.year
    # 通常爬取到去年为止 (例如现在是2026年，则爬取到2025年)
    end_year = current_year - 1
    
    logger.info(f"🚀 开始批量爬取任务: {start_year} 年 至 {end_year} 年")
    
    total_years = 0
    success_count = 0
    
    try:
        for year in range(start_year, end_year + 1):
            total_years += 1
            logger.info(f"\n{'#'*40}")
            logger.info(f"📅 正在处理: {year} 年度榜单")
            logger.info(f"{'#'*40}")
            
            # 使用 crawl_all_tabs 自动爬取该年份所有Tab
            results = crawler.crawl_all_tabs(year=year)
            
            if results:
                count = len(results)
                success_count += 1
                logger.info(f"✅ {year}年度爬取完成，成功获取 {count}/6 个榜单")
            else:
                logger.error(f"❌ {year}年度爬取失败或无数据")
            
            # 年份之间增加较长延时
            time.sleep(5)
                
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
        logger.info(f"📊 总计尝试: {total_years} 个年份")
        logger.info(f"✅ 成功年份: {success_count} 个")
        logger.info(f"📂 数据保存在: {config.OUTPUT_CONFIG['output_dir']}")
        logger.info(f"{'='*50}")

if __name__ == "__main__":
    main()
