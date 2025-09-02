# GitHub部署和版本控制指南

## 🚀 將系統上傳到GitHub

### 📋 準備工作

#### 1. 建立GitHub帳號
如果您還沒有GitHub帳號，請先到 [GitHub.com](https://github.com) 註冊

#### 2. 安裝Git
```bash
# Windows (使用Git for Windows)
# 下載：https://git-scm.com/download/win

# macOS (使用Homebrew)
brew install git

# Ubuntu/Debian
sudo apt-get install git

# 設定Git用戶資訊
git config --global user.name "您的姓名"
git config --global user.email "您的信箱"
```

### 🔧 初始化Git倉庫

#### 1. 在專案目錄中初始化Git
```bash
cd line-card-manager
git init
```

#### 2. 添加所有檔案到Git
```bash
# 添加所有檔案（.gitignore會自動排除不需要的檔案）
git add .

# 提交初始版本
git commit -m "Initial commit: LINE電子名片管理系統 v1.0"
```

#### 3. 在GitHub建立新倉庫
1. 登入GitHub
2. 點擊右上角的「+」→「New repository」
3. 填寫倉庫資訊：
   - **Repository name**: `line-card-manager`
   - **Description**: `專業的LINE電子名片管理系統`
   - **Visibility**: 選擇 Public 或 Private
   - **不要**勾選「Initialize this repository with a README」
4. 點擊「Create repository」

#### 4. 連接本地倉庫到GitHub
```bash
# 添加遠端倉庫（替換為您的GitHub用戶名）
git remote add origin https://github.com/您的用戶名/line-card-manager.git

# 推送到GitHub
git branch -M main
git push -u origin main
```

## 🔄 開發工作流程

### 📝 分支策略

#### 主要分支
- **`main`**: 生產環境，穩定版本
- **`develop`**: 開發環境，整合新功能
- **`feature/*`**: 功能分支，開發新功能
- **`hotfix/*`**: 緊急修復分支

#### 建立開發分支
```bash
# 建立並切換到開發分支
git checkout -b develop

# 推送開發分支到GitHub
git push -u origin develop
```

### 🛠️ 功能開發流程

#### 1. 建立功能分支
```bash
# 從develop分支建立新功能分支
git checkout develop
git pull origin develop
git checkout -b feature/user-authentication

# 開始開發...
```

#### 2. 提交變更
```bash
# 查看變更狀態
git status

# 添加變更檔案
git add src/routes/auth.py
git add src/static/login.html

# 提交變更
git commit -m "feat: 新增用戶認證功能

- 建立登入/登出API
- 新增用戶角色權限管理
- 建立美觀的登入頁面
- 加入session管理功能"
```

#### 3. 推送到GitHub
```bash
# 推送功能分支
git push -u origin feature/user-authentication
```

#### 4. 建立Pull Request
1. 到GitHub倉庫頁面
2. 點擊「Compare & pull request」
3. 填寫PR資訊：
   - **Title**: `feat: 新增用戶認證功能`
   - **Description**: 詳細描述功能和變更
4. 選擇 `develop` 作為目標分支
5. 點擊「Create pull request」

#### 5. 合併到開發分支
```bash
# 切換到develop分支
git checkout develop

# 拉取最新變更
git pull origin develop

# 合併功能分支（如果已在GitHub合併，則跳過）
git merge feature/user-authentication

# 刪除已合併的功能分支
git branch -d feature/user-authentication
git push origin --delete feature/user-authentication
```

## 🌐 自動部署設定

### 🔧 GitHub Actions設定

#### 1. 建立工作流程檔案
```bash
mkdir -p .github/workflows
```

#### 2. 建立部署工作流程
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v3
      with:
        python-version: '3.8'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        python -m pytest tests/ -v
    
    - name: Check code style
      run: |
        flake8 src/ --max-line-length=88

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Deploy to Render
      run: |
        # 這裡可以加入部署腳本
        echo "Deploying to production..."
```

### 🚀 Render.com自動部署

#### 1. 連接GitHub到Render
1. 登入 [Render.com](https://render.com)
2. 點擊「New +」→「Web Service」
3. 選擇「Connect a repository」
4. 授權GitHub並選擇您的倉庫

#### 2. 設定部署參數
- **Name**: `line-card-manager`
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python src/main.py`
- **Auto-Deploy**: `Yes`

#### 3. 設定環境變數
在Render控制台中設定：
```
LINE_CHANNEL_ACCESS_TOKEN=your_token
LINE_CHANNEL_SECRET=your_secret
SECRET_KEY=your_secret_key
FLASK_ENV=production
```

## 📊 版本管理策略

### 🏷️ 版本標籤

#### 語義化版本控制
- **主版本號**: 重大變更，不向後兼容
- **次版本號**: 新功能，向後兼容
- **修訂版本號**: Bug修復，向後兼容

#### 建立版本標籤
```bash
# 建立版本標籤
git tag -a v1.0.0 -m "Release version 1.0.0

新功能:
- 客戶管理系統
- LINE Bot整合
- 專業名片設計器
- 多角色權限管理"

# 推送標籤到GitHub
git push origin v1.0.0
```

### 📝 變更日誌

#### 建立CHANGELOG.md
```markdown
# 變更日誌

## [1.0.0] - 2024-01-15

### 新增
- 客戶管理系統（CRUD操作）
- LINE Bot整合和名片發送
- 專業Flex Message設計器
- 多角色用戶權限管理
- 名片展示廊和統計功能

### 修改
- 優化資料庫結構
- 改進用戶介面設計

### 修復
- 修復名片預覽問題
- 解決登入session問題
```

## 🧪 測試和品質控制

### 📋 測試策略

#### 1. 單元測試
```bash
# 建立測試目錄
mkdir -p tests

# 運行測試
python -m pytest tests/ -v --cov=src
```

#### 2. 整合測試
```bash
# 測試API端點
python -m pytest tests/test_api.py -v

# 測試資料庫操作
python -m pytest tests/test_database.py -v
```

#### 3. 程式碼品質檢查
```bash
# 程式碼格式化
black src/

# 語法檢查
flake8 src/ --max-line-length=88

# 型別檢查
mypy src/
```

### 🔍 程式碼審查

#### Pull Request檢查清單
- [ ] 程式碼遵循PEP 8標準
- [ ] 所有測試通過
- [ ] 新功能有對應的測試
- [ ] 文件已更新
- [ ] 沒有敏感資訊洩露
- [ ] 效能影響評估

## 🚨 問題追蹤和管理

### 🐛 Issue管理

#### Issue標籤系統
- `bug`: 程式錯誤
- `enhancement`: 功能改進
- `feature`: 新功能
- `documentation`: 文件相關
- `help wanted`: 需要協助
- `good first issue`: 適合新手

#### Issue模板
```markdown
## Bug報告

### 描述
簡短描述問題

### 重現步驟
1. 進入...
2. 點擊...
3. 看到錯誤...

### 預期行為
描述預期的正確行為

### 實際行為
描述實際發生的錯誤

### 環境資訊
- OS: [例如 Windows 10]
- Browser: [例如 Chrome 91]
- Python版本: [例如 3.8.5]

### 截圖
如果適用，請添加截圖
```

## 📈 監控和分析

### 📊 GitHub Insights

#### 查看專案統計
- **Code frequency**: 程式碼變更頻率
- **Contributors**: 貢獻者統計
- **Traffic**: 訪問量統計
- **Issues**: 問題處理統計

#### 設定Webhooks
1. 到倉庫設定頁面
2. 點擊「Webhooks」
3. 新增Webhook URL
4. 選擇觸發事件

## 🔐 安全性最佳實踐

### 🛡️ 敏感資訊管理

#### 1. 環境變數
```bash
# 永遠不要提交敏感資訊到Git
echo ".env" >> .gitignore
echo "*.key" >> .gitignore
echo "secrets/" >> .gitignore
```

#### 2. GitHub Secrets
在GitHub倉庫設定中添加：
- `LINE_CHANNEL_ACCESS_TOKEN`
- `LINE_CHANNEL_SECRET`
- `SECRET_KEY`

#### 3. 安全掃描
```yaml
# .github/workflows/security.yml
name: Security Scan

on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Run security scan
      run: |
        pip install safety bandit
        safety check
        bandit -r src/
```

## 🎯 最佳實踐總結

### ✅ 提交訊息規範
```
類型(範圍): 簡短描述

詳細描述（可選）

相關Issue: #123
```

**類型**:
- `feat`: 新功能
- `fix`: Bug修復
- `docs`: 文件更新
- `style`: 程式碼格式
- `refactor`: 重構
- `test`: 測試相關
- `chore`: 建置工具

### 📝 分支命名規範
- `feature/功能名稱`
- `bugfix/問題描述`
- `hotfix/緊急修復`
- `release/版本號`

### 🔄 定期維護
- 每週檢查依賴更新
- 每月檢查安全漏洞
- 每季度程式碼重構
- 每半年架構評估

---

🎉 **恭喜！** 您現在擁有了完整的GitHub版本控制和部署流程！

這個指南將幫助您：
- ✅ 專業地管理程式碼版本
- ✅ 自動化測試和部署
- ✅ 追蹤問題和功能請求
- ✅ 維護高品質的程式碼
- ✅ 安全地管理敏感資訊

開始您的專業開發之旅吧！🚀

