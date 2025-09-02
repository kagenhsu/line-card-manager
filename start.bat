@echo off
chcp 65001 >nul
title LINE電子名片管理系統 - 啟動器

echo ================================================
echo 🎯 LINE電子名片管理系統 - 啟動器
echo ================================================
echo.

:: 檢查Python是否安裝
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 錯誤: 未找到 Python
    echo    請先安裝 Python 3.8 或更高版本
    echo    下載地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: 顯示Python版本
echo ✅ 檢查 Python 版本...
python --version

:: 檢查是否在正確目錄
if not exist "requirements.txt" (
    echo ❌ 錯誤: 找不到 requirements.txt
    echo    請確保在正確的專案目錄中執行此腳本
    pause
    exit /b 1
)

:: 安裝相依套件
echo.
echo 📦 檢查並安裝相依套件...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ 相依套件安裝失敗
    pause
    exit /b 1
)

:: 建立資料庫目錄
if not exist "src\database" mkdir "src\database"

:: 啟動系統
echo.
echo 🚀 啟動系統...
python start.py

pause

