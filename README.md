# LINE電子名片管理系統

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com/)

一個專業的LINE電子名片管理系統，提供完整的客戶管理、名片設計、發送和統計功能。

## 🌟 功能特色

### 📊 **客戶管理系統**
- ✅ 完整的CRUD操作（新增、查詢、修改、刪除）
- ✅ 智能搜尋功能（姓名、公司、電話、信箱）
- ✅ 批量選擇和操作
- ✅ 客戶資料匯入匯出

### 🎨 **專業名片設計器**
- ✅ LINE官方風格的Flex Message設計器
- ✅ 即時預覽功能
- ✅ 多種主題色彩選擇
- ✅ 支援圖片、按鈕、連結等元素

### 📤 **名片匯入管理**
- ✅ 匯入現有Flex Message名片
- ✅ 預設模板庫
- ✅ 批量匯入功能
- ✅ 名片版本控制

### 📱 **LINE Bot整合**
- ✅ 自動發送電子名片給客戶
- ✅ 單一發送和批量發送
- ✅ 發送狀態追蹤
- ✅ LINE官方帳號管理

### 🖼️ **名片展示廊**
- ✅ 美觀的名片展示介面
- ✅ 瀏覽次數統計
- ✅ 分享功能（QR Code、社群媒體）
- ✅ 熱門名片分析

### 👥 **多角色權限管理**
- ✅ **管理員**：完整系統權限
- ✅ **程序員**：技術管理權限
- ✅ **業務員**：客戶管理權限
- ✅ **美工人員**：設計專精權限

## 🚀 快速開始

### 📋 系統需求

- Python 3.8+
- Flask 2.0+
- SQLite 3
- 現代瀏覽器

### 🔧 安裝步驟

#### 1. 克隆倉庫
```bash
git clone https://github.com/your-username/line-card-manager.git
cd line-card-manager
```

#### 2. 建立虛擬環境
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

#### 3. 安裝依賴
```bash
pip install -r requirements.txt
```

#### 4. 初始化資料庫
```bash
python src/main.py
```

#### 5. 訪問系統
開啟瀏覽器訪問：http://localhost:5000

### 🔑 預設帳號

- **用戶名**：`admin`
- **密碼**：`admin123`
- **角色**：管理員

> ⚠️ **重要**：首次登入後請立即修改預設密碼

## 📁 專案結構

```
line-card-manager/
├── src/                          # 主要程式碼
│   ├── static/                   # 靜態檔案
│   │   ├── index.html           # 管理後台主頁
│   │   ├── login.html           # 登入頁面
│   │   ├── flex-card-builder-v2.html  # 專業設計器
│   │   ├── card-gallery.html    # 名片展示廊
│   │   ├── card-import.html     # 名片匯入
│   │   ├── user-management.html # 用戶管理
│   │   ├── styles.css           # 主要樣式
│   │   ├── script.js            # 主要腳本
│   │   └── common-header.css    # 統一頁首樣式
│   ├── models/                   # 資料模型
│   │   ├── user.py              # 用戶模型
│   │   ├── customer.py          # 客戶模型
│   │   ├── auth_user.py         # 認證用戶模型
│   │   └── published_card.py    # 已發布名片模型
│   ├── routes/                   # API路由
│   │   ├── auth.py              # 認證API
│   │   ├── customer.py          # 客戶管理API
│   │   ├── card_publisher.py    # 名片發布API
│   │   └── card_import.py       # 名片匯入API
│   ├── services/                 # 服務層
│   │   └── line_service.py      # LINE Bot服務
│   ├── database/                 # 資料庫檔案
│   └── main.py                  # 主程式入口
├── docs/                         # 文件
├── tests/                        # 測試檔案
├── deployment/                   # 部署腳本
├── requirements.txt              # Python依賴
├── .gitignore                   # Git忽略檔案
├── README.md                    # 專案說明
└── LICENSE                      # 授權條款
```

## 🌐 部署選項

### 🆓 免費雲端部署

#### 1. **Render.com**（推薦新手）
- 每月750小時免費
- 自動SSL憑證
- GitHub整合部署

#### 2. **Railway.app**（最穩定）
- 每月$5額度
- 24/7運行不休眠
- 快速部署

#### 3. **Google Cloud Platform**
- $300免費額度（90天）
- 企業級服務
- 永久免費方案

### 🔧 本地部署

#### 使用一鍵啟動腳本
```bash
# Windows
start.bat

# macOS/Linux
./start.sh

# Python
python start.py
```

## 🛠️ 開發指南

### 🔄 開發流程

1. **Fork專案**到您的GitHub帳號
2. **建立功能分支**：`git checkout -b feature/new-feature`
3. **提交變更**：`git commit -am 'Add new feature'`
4. **推送分支**：`git push origin feature/new-feature`
5. **建立Pull Request**

### 🧪 測試

```bash
# 運行所有測試
python -m pytest

# 運行特定測試
python -m pytest tests/test_customer.py

# 生成覆蓋率報告
python -m pytest --cov=src
```

## 🔧 設定說明

### LINE Bot設定

1. 在[LINE Developers Console](https://developers.line.biz/)建立Bot
2. 獲取Channel Access Token和Channel Secret
3. 在系統中點擊「LINE設定」輸入資訊
4. 測試連線確認設定正確

### 環境變數

建立`.env`檔案：
```env
# LINE Bot設定
LINE_CHANNEL_ACCESS_TOKEN=your_channel_access_token
LINE_CHANNEL_SECRET=your_channel_secret

# 資料庫設定
DATABASE_URL=sqlite:///src/database/app.db

# 安全設定
SECRET_KEY=your_secret_key_here

# 部署設定
FLASK_ENV=production
PORT=5000
```

## 📊 API文件

### 認證API
- `POST /api/auth/login` - 用戶登入
- `POST /api/auth/logout` - 用戶登出
- `GET /api/auth/current-user` - 獲取當前用戶

### 客戶管理API
- `GET /api/customers` - 獲取客戶列表
- `POST /api/customers` - 新增客戶
- `PUT /api/customers/{id}` - 更新客戶
- `DELETE /api/customers/{id}` - 刪除客戶

### 名片管理API
- `POST /api/cards/publish` - 發布名片
- `GET /api/cards/templates` - 獲取模板
- `POST /api/cards/import` - 匯入名片

詳細API文件請參考：[API Documentation](docs/api.md)

## 🤝 貢獻指南

我們歡迎所有形式的貢獻！

### 🐛 回報問題
- 使用[GitHub Issues](https://github.com/your-username/line-card-manager/issues)回報Bug
- 提供詳細的錯誤描述和重現步驟
- 包含系統環境資訊

### 💡 功能建議
- 在Issues中標記為`enhancement`
- 詳細描述功能需求和使用場景
- 提供設計草圖或參考資料

## 📄 授權條款

本專案採用MIT授權條款 - 詳見[LICENSE](LICENSE)檔案

## 🙏 致謝

- [LINE Messaging API](https://developers.line.biz/en/docs/messaging-api/) - LINE Bot功能
- [Flask](https://flask.palletsprojects.com/) - Web框架
- [SQLAlchemy](https://www.sqlalchemy.org/) - 資料庫ORM
- [Font Awesome](https://fontawesome.com/) - 圖示庫

## 📞 支援

- 📧 Email: support@example.com
- 💬 Discord: [加入我們的Discord](https://discord.gg/your-server)
- 📖 文件: [完整文件](https://your-docs-site.com)
- 🐛 問題回報: [GitHub Issues](https://github.com/your-username/line-card-manager/issues)

## 🗺️ 發展路線圖

### v1.1.0 (計劃中)
- [ ] 名片模板市場
- [ ] 進階統計分析
- [ ] 多語言支援
- [ ] 行動APP

### v1.2.0 (未來)
- [ ] AI智能設計建議
- [ ] 客戶關係管理(CRM)
- [ ] 第三方整合(Google Contacts, Outlook)
- [ ] 企業版功能

---

⭐ 如果這個專案對您有幫助，請給我們一個Star！

📢 關注我們獲取最新更新：[GitHub](https://github.com/your-username) | [Twitter](https://twitter.com/your-handle)

