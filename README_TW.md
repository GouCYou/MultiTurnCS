# 多輪對話電商客服系統（Multi-Turn E-commerce Customer Service）

🌎[English](README.md) - [简体中文](README_CN.md) - [繁體中文](README_TW.md)

*以下所有信息均由AI生成，真實性僅供參考*

一個基於 FastAPI + Vue 3 + LangChain + 阿里雲DashScope 的智能電商客服系統，支持商品諮詢、訂單處理、售後維權等全流程多輪對話。

## 🌟 功能特性

### 🤖 AI 客服核心功能
- **多輪對話**：基於 ReAct Agent 模式，支持複雜多輪互動
- **上下文理解**：自動關聯商品信息、訂單狀態
- **智能決策**：動態調用工具處理用戶需求
- **可擴展**：支持接入不同 LLM 模型

### 🛍️ 電商業務功能
- **商品管理**：商品列表、詳情、規格管理
- **訂單系統**：創建訂單、訂單列表、訂單詳情
- **售後處理**：申請退款、售後狀態管理
- **數據持久化**：MySQL 資料庫存儲所有業務數據

### 🎨 技術特性
- **前後端分離**：FastAPI 後端 + Vue 3 前端
- **響應式設計**：支持各種設備訪問
- **RESTful API**：統一的 API 接口設計
- **CORS 支持**：跨域資源共享配置

## 🛠️ 技術棧

### 後端技術棧
| 技術/框架 | 版本 | 用途 |
|---------|------|------|
| FastAPI | 0.115.0 | Web 框架 |
| Uvicorn | 0.30.6 | ASGI 伺服器 |
| Pydantic | 2.6.1 | 數據驗證 |
| PyMySQL | - | MySQL 資料庫連接 |
| LangChain | 0.1.0 | AI 代理框架 |
| DashScope | 1.14.0 | 阿里雲 LLM API |
| numpy | 1.26.4 | 數值計算 |

### 前端技術棧
| 技術/框架 | 版本 | 用途 |
|---------|------|------|
| Vue 3 | 3.4.21 | 前端框架 |
| Vue Router | 4.6.4 | 路由管理 |
| Axios | 1.13.2 | HTTP 請求 |
| Vite | 5.2.0 | 構建工具 |

### 資料庫
| 資料庫 | 版本 | 用途 |
|------|------|------|
| MySQL | 8.0+ | 業務數據存儲 |

## 📦 安裝部署

### 1. 環境準備

- Python 3.10+
- Node.js 16+
- MySQL 8.0+

### 2. 資料庫初始化

1. 創建資料庫：```sql
CREATE DATABASE smart_mall CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
```

2. 匯入資料庫結構：
```bash
mysql -u username -p smart_mall < smart_mall.sql
```

### 3. 後端部署

1. 進入後端目錄：
```bash
cd backend
```

2. 创建虛擬環境：
```bash
python -m venv venv
```

3. 激活虛擬環境：
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

4. 安裝依賴：
```bash
pip install -r requirements.txt
```

5. 配置環境變數（可選，預設配置在 database.py 中）：
```bash
export MYSQL_HOST=localhost
export MYSQL_PORT=3306
export MYSQL_USER=root
export MYSQL_PASSWORD=password
export MYSQL_DB=smart_mall
```

6. 啟動後端服務：
```bash
uvicorn api_server:app --reload --host 0.0.0.0 --port 8000
```

### 4. 前端部署

1. 進入前端目錄：
```bash
cd frontend
```

2. 安裝依賴：
```bash
npm install
```

3. 啟動開發伺服器：
```bash
npm run dev
```

4. 建立生產版本（可選）：
```bash
npm run build
```

## 🚀 使用說明

### 1. 訪問系統

- 前端：`http://localhost:5173`
- 後端 API：`http://localhost:8000`
- API 文檔：`http://localhost:8000/docs`

### 2. AI 客服對話

1. 訪問前端頁面
2. 選擇商品或輸入訂單號（可選，用於提供上下文）
3. 輸入您的問題，例如：
   - "這個商品有哪些顏色？"
   - "我的訂單什麼時候發貨？"
   - "我想申請退款"
4. 系統將自動處理您的請求並給出回應

### 3. API 接口調用

示例：調用 AI 客服接口

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "这个商品有什么颜色？", "product_id": "P12345678"}'
```

## 📖 API 文档

### 健康檢查
- `GET /health` - 檢查服務狀態

### AI 客服
- `POST /chat` - 發送對話請求

### 商品管理
- `GET /api/products` - 獲取商品列表
- `GET /api/products/{pid}` - 獲取商品詳情
- `POST /api/admin/products` - 創建商品
- `PUT /api/admin/products/{pid}` - 更新商品
- `DELETE /api/admin/products/{pid}` - 刪除商品

### 訂單管理
- `POST /api/orders` - 創建訂單
- `GET /api/orders` - 獲取訂單列表
- `GET /api/orders/{order_no}` - 獲取訂單詳情
- `POST /api/orders/{order_no}/refund` - 申請退款
- `DELETE /api/orders/{order_no}` - 刪除訂單

### 管理員接口
- `PATCH /api/admin/orders/{order_no}` - 更新訂單狀態
- `DELETE /api/admin/orders/{order_no}` - 管理員刪除訂單

## 🔧 配置說明

### 後端配置

#### 資料庫配置
在 `backend/database.py` 中配置資料庫連接：

```python
MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "password")
MYSQL_DB = os.getenv("MYSQL_DB", "smart_mall")
```

#### LLM 配置
在 `backend/api_server.py` 中配置 LLM：

```python
DASHSCOPE_API_KEY = "your-api-key"
ALIYUN_MODEL_NAME = "qwen-turbo"
ALIYUN_TEMPERATURE = 0.2
```

### 前端配置

在 `frontend/src/api/backend.js` 中配置 API 地址：

```javascript
const api = axios.create({
  baseURL: "http://127.0.0.1:8000",
  timeout: 10000
});
```

## 📊 資料庫結構

### 核心表結構

#### products（商品表）
- product_id: 商品 ID
- shop_id: 店鋪 ID
- title: 商品標題
- category: 商品分類
- price: 商品價格
- description: 商品描述
- specs: 商品規格
- image_url: 商品主圖
- carousel_images: 輪播圖
- detail_images:  詳情圖

#### orders（訂單表）
- order_no: 訂單號
- status: 訂單狀態（PAID, SHIPPED, DELIVERED, REFUNDING, REFUNDED）
- receiver: 收件人
- phone_tail: 手機號尾號
- total_amount: 訂單金額

#### order_items（訂單項表）
- order_id: 訂單 ID
- product_id: 商品 ID
- title: 商品標題
- price: 商品價格
- qty: 商品數量

#### after_sales（售後表）
- after_sale_no: 售後單號
- order_no: 關聯訂單號
- type: 售後類型
- reason: 售後原因
- status: 售後狀態

## 🔍 核心功能實現

### ReAct Agent 實現

系統使用 LangChain 的 ReAct Agent 模式實現智能客服，核心代碼在 `backend/agent/react_agent.py`：

1. 定義工具：商品查詢、訂單查詢等
2. 構建 Agent：集成 LLM 和工具
3. 執行對話：處理用戶輸入並生成響應

### 上下文管理

系統自動處理上下文信息：
- 商品上下文：當提供 product_id 時，自動加載商品信息
- 訂單上下文：當提供 order_no 時，自動加載訂單信息
- 對話歷史：維護多輪對話歷史

## 🤝 贡献指南

歡迎提交 Issue 和 Pull Request！

### 開發流程

1. Fork 倉庫
2. 創建特性分支：`git checkout -b feature/AmazingFeature`
3. 提交更改：`git commit -m 'Add some AmazingFeature'`
4. 推送到分支：`git push origin feature/AmazingFeature`
5. 提交 Pull Request

## 📄 许可证

本項目採用 MIT 許可證 - 查看 [LICENSE](LICENSE) 文件了解詳情。

## 📞 聯繫方式

如有問題或建議，請提交 Issue 或聯繫項目維護者。

---

**Star ⭐ 這個項目，如果它對您有幫助！**