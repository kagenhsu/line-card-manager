# API 文件

## 概述

LINE電子名片管理系統提供RESTful API，支援客戶管理、用戶認證、名片設計和LINE Bot整合等功能。

## 基本資訊

- **Base URL**: `https://your-domain.com/api`
- **認證方式**: Session-based authentication
- **資料格式**: JSON
- **字元編碼**: UTF-8

## 認證 API

### 用戶登入

```http
POST /api/auth/login
```

**請求參數**:
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**回應**:
```json
{
  "success": true,
  "message": "登入成功",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "full_name": "系統管理員",
    "role": "admin",
    "role_name": "管理員",
    "permissions": {
      "customer_management": true,
      "card_design": true,
      "card_import": true,
      "user_management": true,
      "system_config": true,
      "statistics": true
    }
  }
}
```

### 用戶登出

```http
POST /api/auth/logout
```

**回應**:
```json
{
  "success": true,
  "message": "登出成功"
}
```

### 獲取當前用戶

```http
GET /api/auth/current-user
```

**回應**:
```json
{
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "full_name": "系統管理員",
    "role": "admin",
    "role_name": "管理員",
    "permissions": {...}
  }
}
```

## 客戶管理 API

### 獲取客戶列表

```http
GET /api/customers
```

**查詢參數**:
- `page` (可選): 頁碼，預設為1
- `per_page` (可選): 每頁數量，預設為20
- `sort` (可選): 排序欄位，預設為created_at
- `order` (可選): 排序方向，asc或desc，預設為desc

**回應**:
```json
{
  "customers": [
    {
      "id": 1,
      "name": "張三",
      "phone": "0912345678",
      "email": "zhang@example.com",
      "company": "ABC公司",
      "position": "經理",
      "line_user_id": "U1234567890",
      "website": "https://abc.com",
      "facebook_url": "https://facebook.com/abc",
      "google_map_url": "https://maps.google.com/abc",
      "contract_end_date": "2024-12-31",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z",
      "has_card": true,
      "card_views": 25
    }
  ],
  "total": 1,
  "page": 1,
  "per_page": 20,
  "pages": 1
}
```

### 新增客戶

```http
POST /api/customers
```

**請求參數**:
```json
{
  "name": "張三",
  "phone": "0912345678",
  "email": "zhang@example.com",
  "company": "ABC公司",
  "position": "經理",
  "line_user_id": "U1234567890",
  "address": "台北市信義區",
  "website": "https://abc.com",
  "facebook_url": "https://facebook.com/abc",
  "google_map_url": "https://maps.google.com/abc",
  "notes": "重要客戶",
  "contract_end_date": "2024-12-31"
}
```

**回應**:
```json
{
  "success": true,
  "message": "客戶新增成功",
  "customer": {
    "id": 1,
    "name": "張三",
    ...
  }
}
```

### 更新客戶

```http
PUT /api/customers/{id}
```

**請求參數**: 同新增客戶

**回應**:
```json
{
  "success": true,
  "message": "客戶更新成功",
  "customer": {
    "id": 1,
    "name": "張三",
    ...
  }
}
```

### 刪除客戶

```http
DELETE /api/customers/{id}
```

**回應**:
```json
{
  "success": true,
  "message": "客戶刪除成功"
}
```

### 搜尋客戶

```http
GET /api/customers/search?q={keyword}
```

**查詢參數**:
- `q`: 搜尋關鍵字（搜尋姓名、公司、電話、信箱）

**回應**:
```json
{
  "customers": [...],
  "total": 5,
  "keyword": "張"
}
```

## 名片管理 API

### 發布名片

```http
POST /api/cards/publish
```

**請求參數**:
```json
{
  "customer_id": 1,
  "card_data": {
    "type": "flex",
    "altText": "電子名片",
    "contents": {
      "type": "bubble",
      "body": {
        "type": "box",
        "layout": "vertical",
        "contents": [...]
      }
    }
  },
  "title": "張三的電子名片",
  "description": "ABC公司經理"
}
```

**回應**:
```json
{
  "success": true,
  "message": "名片發布成功",
  "card": {
    "id": 1,
    "share_url": "https://your-domain.com/card/abc123",
    "qr_code_url": "https://your-domain.com/qr/abc123.png",
    "views": 0
  }
}
```

### 獲取名片模板

```http
GET /api/cards/templates
```

**回應**:
```json
{
  "templates": [
    {
      "id": "business_card_1",
      "name": "商務名片模板",
      "description": "適合商務人士使用的專業名片",
      "preview_image": "https://example.com/preview1.jpg",
      "card_data": {...}
    }
  ]
}
```

### 匯入名片

```http
POST /api/cards/import
```

**請求參數**:
```json
{
  "customer_id": 1,
  "flex_message": {
    "type": "flex",
    "altText": "電子名片",
    "contents": {...}
  },
  "title": "匯入的名片"
}
```

**回應**:
```json
{
  "success": true,
  "message": "名片匯入成功",
  "card": {
    "id": 1,
    "share_url": "https://your-domain.com/card/abc123"
  }
}
```

## LINE Bot API

### 發送名片給單一客戶

```http
POST /api/line/send-card/{customer_id}
```

**回應**:
```json
{
  "success": true,
  "message": "名片發送成功",
  "line_response": {
    "sentMessages": [...]
  }
}
```

### 批量發送名片

```http
POST /api/line/send-card-batch
```

**請求參數**:
```json
{
  "customer_ids": [1, 2, 3, 4, 5]
}
```

**回應**:
```json
{
  "success": true,
  "message": "批量發送完成",
  "results": {
    "sent": 4,
    "failed": 1,
    "details": [
      {
        "customer_id": 1,
        "status": "success"
      },
      {
        "customer_id": 2,
        "status": "failed",
        "error": "LINE User ID not found"
      }
    ]
  }
}
```

### 預覽客戶名片

```http
GET /api/line/preview-card/{customer_id}
```

**回應**:
```json
{
  "preview": {
    "type": "flex",
    "altText": "張三的電子名片",
    "contents": {...}
  }
}
```

### 檢查LINE設定

```http
GET /api/line/config
```

**回應**:
```json
{
  "configured": true,
  "channel_name": "我的LINE Bot",
  "webhook_url": "https://your-domain.com/webhook",
  "status": "active"
}
```

## 統計 API

### 獲取系統統計

```http
GET /api/stats/overview
```

**回應**:
```json
{
  "customers": {
    "total": 150,
    "new_this_month": 12,
    "active": 145
  },
  "cards": {
    "total": 89,
    "published": 76,
    "total_views": 1250
  },
  "line_messages": {
    "sent_today": 25,
    "sent_this_month": 340,
    "success_rate": 0.95
  }
}
```

## 錯誤處理

### 錯誤回應格式

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "請求參數驗證失敗",
    "details": {
      "name": ["姓名為必填欄位"],
      "email": ["電子郵件格式不正確"]
    }
  }
}
```

### 常見錯誤代碼

| 代碼 | HTTP狀態 | 說明 |
|------|----------|------|
| `VALIDATION_ERROR` | 400 | 請求參數驗證失敗 |
| `UNAUTHORIZED` | 401 | 未認證或認證失敗 |
| `FORBIDDEN` | 403 | 權限不足 |
| `NOT_FOUND` | 404 | 資源不存在 |
| `CONFLICT` | 409 | 資源衝突（如重複的電子郵件） |
| `RATE_LIMIT_EXCEEDED` | 429 | 請求頻率超過限制 |
| `INTERNAL_ERROR` | 500 | 伺服器內部錯誤 |
| `LINE_API_ERROR` | 502 | LINE API呼叫失敗 |

## 速率限制

- **一般API**: 每分鐘100次請求
- **LINE發送API**: 每分鐘10次請求
- **認證API**: 每分鐘5次請求

超過限制時會回傳HTTP 429狀態碼。

## 版本控制

API版本透過URL路徑指定：
- 當前版本: `/api/v1/`
- 舊版本將持續支援至少6個月

## SDK和範例

### JavaScript範例

```javascript
// 登入
const login = async (username, password) => {
  const response = await fetch('/api/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ username, password }),
  });
  return response.json();
};

// 獲取客戶列表
const getCustomers = async () => {
  const response = await fetch('/api/customers');
  return response.json();
};

// 新增客戶
const createCustomer = async (customerData) => {
  const response = await fetch('/api/customers', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(customerData),
  });
  return response.json();
};
```

### Python範例

```python
import requests

class LineCardAPI:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()
    
    def login(self, username, password):
        response = self.session.post(
            f'{self.base_url}/api/auth/login',
            json={'username': username, 'password': password}
        )
        return response.json()
    
    def get_customers(self):
        response = self.session.get(f'{self.base_url}/api/customers')
        return response.json()
    
    def create_customer(self, customer_data):
        response = self.session.post(
            f'{self.base_url}/api/customers',
            json=customer_data
        )
        return response.json()

# 使用範例
api = LineCardAPI('https://your-domain.com')
api.login('admin', 'password')
customers = api.get_customers()
```

## 支援

如有API相關問題，請聯繫：
- 📧 Email: api-support@example.com
- 📖 文件: https://docs.your-domain.com
- 🐛 問題回報: https://github.com/your-username/line-card-manager/issues

