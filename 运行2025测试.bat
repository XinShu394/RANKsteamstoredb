@echo off
chcp 65001
echo ========================================
echo   Steam 2025年榜单数据测试
echo ========================================
echo.
cd /d "%~dp0"
python test_run_2025.py
pause
