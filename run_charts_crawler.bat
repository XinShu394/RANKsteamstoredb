@echo off
chcp 65001 > nul
title Steam Charts 榜单爬虫 V1.0.0

echo.
echo ========================================
echo     Steam Charts 榜单爬虫 V1.0.0
echo ========================================
echo.

cd /d "%~dp0"

python run_charts_crawler.py

if %errorlevel% neq 0 (
    echo.
    echo ❌ 程序运行出错！
    pause
)
