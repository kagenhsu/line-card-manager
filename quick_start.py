#!/usr/bin/env python3
"""
LINE電子名片管理系統 - 快速啟動腳本
解決啟動問題的簡化版本
"""

import os
import sys
import subprocess
import webbrowser
import time
from pathlib import Path

def print_header():
    """顯示標題"""
    print("=" * 60)
    print("🎯 LINE電子名片管理系統 - 快速啟動器")
    print("=" * 60)

def check_python():
    """檢查Python版本"""
    print("🔍 檢查Python環境...")
    
    if sys.version_info < (3, 6):
        print(f"❌ Python版本過低: {sys.version}")
        print("   需要Python 3.6或更高版本")
        return False
    
    print(f"✅ Python版本: {sys.version.split()[0]}")
    return True

def install_requirements():
    """安裝必要套件"""
    print("📦 檢查並安裝套件...")
    
    required_packages = ['flask', 'flask-sqlalchemy', 'flask-cors']
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package} 已安裝")
        except ImportError:
            print(f"📥 正在安裝 {package}...")
            try:
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", package
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print(f"✅ {package} 安裝完成")
            except subprocess.CalledProcessError:
                print(f"❌ {package} 安裝失敗")
                return False
    
    return True

def setup_directories():
    """建立必要目錄"""
    print("📁 建立目錄結構...")
    
    base_dir = Path(__file__).parent
    dirs_to_create = [
        base_dir / "src" / "database",
        base_dir / "src" / "static"
    ]
    
    for dir_path in dirs_to_create:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    print("✅ 目錄結構已準備")

def start_server():
    """啟動伺服器"""
    print("🚀 啟動伺服器...")
    
    # 使用簡化版主程式
    main_file = Path(__file__).parent / "src" / "main_simple.py"
    
    if not main_file.exists():
        print("❌ 找不到主程式檔案")
        return None
    
    try:
        # 設定工作目錄
        work_dir = Path(__file__).parent
        
        # 啟動伺服器
        process = subprocess.Popen([
            sys.executable, str(main_file)
        ], cwd=str(work_dir))
        
        return process
    except Exception as e:
        print(f"❌ 啟動失敗: {e}")
        return None

def wait_for_server(timeout=30):
    """等待伺服器啟動"""
    print("⏳ 等待伺服器啟動...")
    
    import urllib.request
    import urllib.error
    
    for i in range(timeout):
        try:
            response = urllib.request.urlopen("http://localhost:5000/api/health", timeout=2)
            if response.getcode() == 200:
                print("✅ 伺服器已啟動")
                return True
        except (urllib.error.URLError, OSError):
            pass
        
        time.sleep(1)
        if i % 5 == 0 and i > 0:
            print(f"   等待中... ({i}/{timeout}秒)")
    
    print("⚠️ 伺服器啟動可能需要更多時間")
    return False

def open_browser():
    """開啟瀏覽器"""
    print("🌐 開啟瀏覽器...")
    
    urls = [
        ("管理後台", "http://localhost:5000"),
        ("專業設計器", "http://localhost:5000/flex-card-builder.html"),
        ("名片展示廊", "http://localhost:5000/card-gallery.html")
    ]
    
    # 開啟主頁面
    webbrowser.open("http://localhost:5000")
    
    print("\n🎉 系統啟動成功！")
    print("📋 可用頁面:")
    for name, url in urls:
        print(f"   {name}: {url}")

def main():
    """主函數"""
    print_header()
    
    # 檢查Python
    if not check_python():
        input("\n按 Enter 鍵退出...")
        return
    
    # 安裝套件
    if not install_requirements():
        print("\n❌ 套件安裝失敗，請手動執行:")
        print("   pip install flask flask-sqlalchemy flask-cors")
        input("\n按 Enter 鍵退出...")
        return
    
    # 建立目錄
    setup_directories()
    
    # 啟動伺服器
    server_process = start_server()
    if not server_process:
        input("\n按 Enter 鍵退出...")
        return
    
    # 等待伺服器啟動
    if wait_for_server():
        time.sleep(2)  # 額外等待確保完全啟動
        open_browser()
    else:
        print("🌐 請手動開啟: http://localhost:5000")
    
    print("\n" + "=" * 60)
    print("💡 使用說明:")
    print("   - 系統正在背景運行")
    print("   - 按 Ctrl+C 停止系統")
    print("   - 關閉此視窗將停止系統")
    print("=" * 60)
    
    try:
        # 保持程式運行
        print("\n⏳ 系統運行中，按 Ctrl+C 停止...")
        server_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 正在停止系統...")
        server_process.terminate()
        try:
            server_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server_process.kill()
        print("✅ 系統已停止")

if __name__ == "__main__":
    main()

