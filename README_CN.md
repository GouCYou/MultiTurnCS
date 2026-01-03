# 多轮对话电商客服系统（Multi-Turn E-commerce Customer Service）

🌎[English](README.md) - [简体中文](README_CN.md) - [繁體中文](README_TW.md)

*以下所有信息均由AI生成，真实性仅供参考*

一个基于 FastAPI + Vue 3 + LangChain + 阿里云DashScope 的智能电商客服系统，支持商品咨询、订单处理、售后维权等全流程多轮对话。

## 🌟 功能特性

### 🤖 AI 客服核心功能
- **多轮对话**：基于 ReAct Agent 模式，支持复杂多轮交互
- **上下文理解**：自动关联商品信息、订单状态
- **智能决策**：动态调用工具处理用户需求
- **可扩展**：支持接入不同 LLM 模型

### 🛍️ 电商业务功能
- **商品管理**：商品列表、详情、规格管理
- **订单系统**：创建订单、订单列表、订单详情
- **售后处理**：申请退款、售后状态管理
- **数据持久化**：MySQL 数据库存储所有业务数据

### 🎨 技术特性
- **前后端分离**：FastAPI 后端 + Vue 3 前端
- **响应式设计**：支持各种设备访问
- **RESTful API**：统一的 API 接口设计
- **CORS 支持**：跨域资源共享配置

## 🛠️ 技术栈

### 后端技术栈
| 技术/框架 | 版本 | 用途 |
|---------|------|------|
| FastAPI | 0.115.0 | Web 框架 |
| Uvicorn | 0.30.6 | ASGI 服务器 |
| Pydantic | 2.6.1 | 数据验证 |
| PyMySQL | - | MySQL 数据库连接 |
| LangChain | 0.1.0 | AI 代理框架 |
| DashScope | 1.14.0 | 阿里云 LLM API |
| numpy | 1.26.4 | 数值计算 |

### 前端技术栈
| 技术/框架 | 版本 | 用途 |
|---------|------|------|
| Vue 3 | 3.4.21 | 前端框架 |
| Vue Router | 4.6.4 | 路由管理 |
| Axios | 1.13.2 | HTTP 请求 |
| Vite | 5.2.0 | 构建工具 |

### 数据库
| 数据库 | 版本 | 用途 |
|------|------|------|
| MySQL | 8.0+ | 业务数据存储 |

## 📦 安装部署

### 1. 环境准备

- Python 3.10+
- Node.js 16+
- MySQL 8.0+

### 2. 数据库初始化

1. 创建数据库：
```sql
CREATE DATABASE smart_mall CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
```

2. 导入数据库结构：
```bash
mysql -u username -p smart_mall < smart_mall.sql
```

### 3. 后端部署

1. 进入后端目录：
```bash
cd backend
```

2. 创建虚拟环境：
```bash
python -m venv venv
```

3. 激活虚拟环境：
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

4. 安装依赖：
```bash
pip install -r requirements.txt
```

5. 配置环境变量（可选，默认配置在 database.py 中）：
```bash
export MYSQL_HOST=localhost
export MYSQL_PORT=3306
export MYSQL_USER=root
export MYSQL_PASSWORD=password
export MYSQL_DB=smart_mall
```

6. 启动后端服务：
```bash
uvicorn api_server:app --reload --host 0.0.0.0 --port 8000
```

### 4. 前端部署

1. 进入前端目录：
```bash
cd frontend
```

2. 安装依赖：
```bash
npm install
```

3. 启动开发服务器：
```bash
npm run dev
```

4. 构建生产版本（可选）：
```bash
npm run build
```

## 🚀 使用说明

### 1. 访问系统

- 前端：`http://localhost:5173`
- 后端 API：`http://localhost:8000`
- API 文档：`http://localhost:8000/docs`

### 2. AI 客服对话

1. 访问前端页面
2. 选择商品或输入订单号（可选，用于提供上下文）
3. 输入您的问题，例如：
   - "这个商品有什么颜色？"
   - "我的订单什么时候发货？"
   - "我想申请退款"
4. 系统将自动处理您的请求并给出响应

### 3. API 接口调用

示例：调用 AI 客服接口

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "这个商品有什么颜色？", "product_id": "P12345678"}'
```

## 📖 API 文档

### 健康检查
- `GET /health` - 检查服务状态

### AI 客服
- `POST /chat` - 发送对话请求

### 商品管理
- `GET /api/products` - 获取商品列表
- `GET /api/products/{pid}` - 获取商品详情
- `POST /api/admin/products` - 创建商品
- `PUT /api/admin/products/{pid}` - 更新商品
- `DELETE /api/admin/products/{pid}` - 删除商品

### 订单管理
- `POST /api/orders` - 创建订单
- `GET /api/orders` - 获取订单列表
- `GET /api/orders/{order_no}` - 获取订单详情
- `POST /api/orders/{order_no}/refund` - 申请退款
- `DELETE /api/orders/{order_no}` - 删除订单

### 管理员接口
- `PATCH /api/admin/orders/{order_no}` - 更新订单状态
- `DELETE /api/admin/orders/{order_no}` - 管理员删除订单

## 🔧 配置说明

### 后端配置

#### 数据库配置
在 `backend/database.py` 中配置数据库连接：

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

## 📊 数据库结构

### 核心表结构

#### products（商品表）
- product_id: 商品ID
- shop_id: 店铺ID
- title: 商品标题
- category: 商品分类
- price: 商品价格
- description: 商品描述
- specs: 商品规格
- image_url: 商品主图
- carousel_images: 轮播图
- detail_images: 详情图

#### orders（订单表）
- order_no: 订单号
- status: 订单状态（PAID, SHIPPED, DELIVERED, REFUNDING, REFUNDED）
- receiver: 收件人
- phone_tail: 手机号尾号
- total_amount: 订单金额

#### order_items（订单项表）
- order_id: 订单ID
- product_id: 商品ID
- title: 商品标题
- price: 商品价格
- qty: 商品数量

#### after_sales（售后表）
- after_sale_no: 售后单号
- order_no: 关联订单号
- type: 售后类型
- reason: 售后原因
- status: 售后状态

## 🔍 核心功能实现

### ReAct Agent 实现

系统使用 LangChain 的 ReAct Agent 模式实现智能客服，核心代码在 `backend/agent/react_agent.py`：

1. 定义工具：商品查询、订单查询等
2. 构建 Agent：集成 LLM 和工具
3. 执行对话：处理用户输入并生成响应

### 上下文管理

系统自动处理上下文信息：
- 商品上下文：当提供 product_id 时，自动加载商品信息
- 订单上下文：当提供 order_no 时，自动加载订单信息
- 对话历史：维护多轮对话历史

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

### 开发流程

1. Fork 仓库
2. 创建特性分支：`git checkout -b feature/AmazingFeature`
3. 提交更改：`git commit -m 'Add some AmazingFeature'`
4. 推送到分支：`git push origin feature/AmazingFeature`
5. 提交 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 联系方式

如有问题或建议，请提交 Issue 或联系项目维护者。

---

**Star ⭐ 这个项目，如果它对您有帮助！**