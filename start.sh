#!/bin/bash

# LINE電子名片管理系統 - 啟動腳本 (Linux/macOS)

echo "================================================"
echo "🎯 LINE電子名片管理系統 - 啟動器"
echo "================================================"
echo

# 檢查Python是否安裝
if ! command -v python3 &> /dev/null; then
    echo "❌ 錯誤: 未找到 Python3"
    echo "   請先安裝 Python 3.8 或更高版本"
    exit 1
fi

# 顯示Python版本
echo "✅ 檢查 Python 版本..."
python3 --version

# 檢查是否在正確目錄
if [ ! -f "requirements.txt" ]; then
    echo "❌ 錯誤: 找不到 requirements.txt"
    echo "   請確保在正確的專案目錄中執行此腳本"
    exit 1
fi

# 建立虛擬環境（如果不存在）
if [ ! -d "venv" ]; then
    echo "📦 建立虛擬環境..."
    python3 -m venv venv
fi

# 啟動虛擬環境
echo "🔧 啟動虛擬環境..."
source venv/bin/activate

# 安裝相依套件
echo "📥 安裝相依套件..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ 相依套件安裝失敗"
    exit 1
fi

# 建立資料庫目錄
mkdir -p src/database

# 啟動系統
echo
echo "🚀 啟動系統..."
python3 start.py

