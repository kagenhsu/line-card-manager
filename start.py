#!/usr/bin/env python3
"""
LINE電子名片管理系統 - 啟動腳本
"""

import os
import sys
import subprocess
import webbrowser
import time
import threading
from pathlib import Path

def check_python_version():
    """檢查Python版本"""
    if sys.version_info < (3, 8):
        print("❌ 錯誤: 需要 Python 3.8 或更高版本")
        print(f"   當前版本: {sys.version}")
        return False
    print(f"✅ Python 版本: {sys.version.split()[0]}")
    return True

def check_requirements():
    """檢查並安裝相依套件"""
    requirements_file = Path(__file__).parent / "requirements.txt"
    
    if not requirements_file.exists():
        print("❌ 找不到 requirements.txt 檔案")
        return False
    
    print("📦 檢查相依套件...")
    
    try:
        # 檢查是否已安裝 Flask
        import flask
        print("✅ Flask 已安裝")
    except ImportError:
        print("📥 正在安裝相依套件...")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
            ])
            print("✅ 相依套件安裝完成")
        except subprocess.CalledProcessError:
            print("❌ 相依套件安裝失敗")
            return False
    
    return True

def setup_database():
    """設定資料庫"""
    db_dir = Path(__file__).parent / "src" / "database"
    db_dir.mkdir(exist_ok=True)
    print("✅ 資料庫目錄已準備")

def start_flask_server():
    """啟動Flask伺服器"""
    src_dir = Path(__file__).parent / "src"
    main_file = src_dir / "main.py"
    
    if not main_file.exists():
        print("❌ 找不到 main.py 檔案")
        return None
    
    print("🚀 啟動 Flask 伺服器...")
    
    try:
        # 設定環境變數
        env = os.environ.copy()
        env['PYTHONPATH'] = str(src_dir.parent)
        
        # 啟動伺服器
        process = subprocess.Popen([
            sys.executable, str(main_file)
        ], env=env, cwd=str(src_dir.parent))
        
        return process
    except Exception as e:
        print(f"❌ 啟動伺服器失敗: {e}")
        return None

def wait_for_server(timeout=30):
    """等待伺服器啟動"""
    import urllib.request
    import urllib.error
    
    print("⏳ 等待伺服器啟動...")
    
    for i in range(timeout):
        try:
            urllib.request.urlopen("http://localhost:5000", timeout=1)
            print("✅ 伺服器已啟動")
            return True
        except (urllib.error.URLError, OSError):
            time.sleep(1)
            if i % 5 == 0:
                print(f"   等待中... ({i}/{timeout}秒)")
    
    print("❌ 伺服器啟動超時")
    return False

def open_launcher():
    """開啟啟動器頁面"""
    launcher_file = Path(__file__).parent / "launcher.html"
    
    if launcher_file.exists():
        launcher_url = f"file://{launcher_file.absolute()}"
        print(f"🌐 開啟啟動器: {launcher_url}")
        webbrowser.open(launcher_url)
    else:
        print("🌐 開啟管理後台: http://localhost:5000")
        webbrowser.open("http://localhost:5000")

def main():
    """主函數"""
    print("=" * 50)
    print("🎯 LINE電子名片管理系統 - 啟動器")
    print("=" * 50)
    
    # 檢查Python版本
    if not check_python_version():
        input("按 Enter 鍵退出...")
        return
    
    # 檢查相依套件
    if not check_requirements():
        input("按 Enter 鍵退出...")
        return
    
    # 設定資料庫
    setup_database()
    
    # 啟動伺服器
    server_process = start_flask_server()
    if not server_process:
        input("按 Enter 鍵退出...")
        return
    
    # 等待伺服器啟動
    if wait_for_server():
        # 開啟瀏覽器
        time.sleep(2)  # 等待2秒確保伺服器完全啟動
        open_launcher()
        
        print("\n" + "=" * 50)
        print("🎉 系統啟動成功！")
        print("📱 管理後台: http://localhost:5000")
        print("🎨 專業設計器: http://localhost:5000/flex-card-builder.html")
        print("🖼️ 名片展示廊: http://localhost:5000/card-gallery.html")
        print("=" * 50)
        print("\n💡 提示:")
        print("   - 按 Ctrl+C 停止系統")
        print("   - 關閉此視窗將停止系統")
        print("   - 系統運行時請保持此視窗開啟")
        
        try:
            # 保持程式運行
            server_process.wait()
        except KeyboardInterrupt:
            print("\n🛑 正在停止系統...")
            server_process.terminate()
            server_process.wait()
            print("✅ 系統已停止")
    else:
        print("❌ 系統啟動失敗")
        server_process.terminate()
        input("按 Enter 鍵退出...")

if __name__ == "__main__":
    main()

