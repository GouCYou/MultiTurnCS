# api_server.py
import json
from fastapi import HTTPException

from fastapi.staticfiles import StaticFiles
from fastapi import UploadFile, File, Form

from datetime import datetime
from backend.database import get_conn

from fastapi.responses import FileResponse
import os
import uuid
from typing import Dict, List, Optional, Any

from fastapi import FastAPI
from pydantic import BaseModel, Field

# ReAct Agent
from backend.agent.react_agent import build_agent, run_agent

# 阿里 DashScope
import dashscope
from langchain.llms.base import LLM


# 阿里云百炼 Key
DASHSCOPE_API_KEY = "your_dashscope_api_key"
ALIYUN_MODEL_NAME = "qwen-turbo"
ALIYUN_TEMPERATURE = 0.2


class AliyunQwenLLM(LLM):

    model_name: str = ALIYUN_MODEL_NAME
    temperature: float = ALIYUN_TEMPERATURE

    @property
    def _llm_type(self) -> str:
        return "aliyun_qwen"

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        resp = dashscope.Generation.call(
            api_key=DASHSCOPE_API_KEY,
            model=self.model_name,
            prompt=prompt,
            temperature=self.temperature,
            result_format="text",
        )

        if resp.status_code != 200:
            raise RuntimeError(f"DashScope error: {resp}")

        text = resp.output.text or ""

        if stop:
            for s in stop:
                if s and s in text:
                    text = text.split(s)[0]
        return text


app = FastAPI(title="多轮电商客服模拟器（ReAct + Tools）")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 访问: http://127.0.0.1:8000/uploads/xxx.jpg
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


def _load_json(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_shops():
    # 数据库中没有shops表，返回空列表
    return []

def get_shop_by_id(shop_id: str):
    # 数据库中没有shops表，返回None
    return None

def get_product_by_id(product_id: str):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT product_id, shop_id, title, category, price, description, specs_json, image_url, carousel_images, detail_images, detailed_text, is_active "
                "FROM products WHERE product_id=%s LIMIT 1",
                (product_id,),
            )
            r = cur.fetchone()
            if r:
                try:
                    r["specs"] = json.loads(r["specs_json"]) if r.get("specs_json") else {}
                except Exception:
                    r["specs"] = {}
                r.pop("specs_json", None)
                # Handle JSON fields
                if r.get("carousel_images"):
                    try:
                        r["carousel_images"] = json.loads(r["carousel_images"]) if isinstance(r["carousel_images"], str) else r["carousel_images"]
                    except:
                        r["carousel_images"] = []
                else:
                    r["carousel_images"] = []
                if r.get("detail_images"):
                    try:
                        r["detail_images"] = json.loads(r["detail_images"]) if isinstance(r["detail_images"], str) else r["detail_images"]
                    except:
                        r["detail_images"] = []
                else:
                    r["detail_images"] = []
                return r

    for p in load_products():
        if p["product_id"] == product_id:
            return p
    return None

# @app.get("/")
# def index():
#     return FileResponse(os.path.join(BASE_DIR, "web", "index.html"))

# session_id -> [{"role":"user|assistant","content":"..."}]
SESSIONS: Dict[str, List[Dict[str, str]]] = {}

class ChatRequest(BaseModel):
    session_id: Optional[str] = Field(default=None, description="不传则自动创建")
    message: str = Field(..., description="用户输入")
    reset: bool = Field(default=False, description="是否清空该 session 记录")
    product_id: Optional[str] = Field(default=None, description="当前商品ID（可选）")
    shop_id: Optional[str] = Field(default=None, description="当前店铺ID（可选）")
    order_no: Optional[str] = Field(default=None, description="当前订单号（可选）")

class StepItem(BaseModel):
    action: str
    observation: str


class ChatResponse(BaseModel):
    session_id: str
    answer: str
    steps: List[StepItem]


@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/api/shops")
def api_shops():
    # 数据库中没有shops表，返回空列表
    return []

@app.get("/api/products")
def api_products():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT product_id, shop_id, title, category, price, description, specs_json, image_url, carousel_images, is_active "
                "FROM products WHERE is_active=1 ORDER BY id DESC"
            )
            rows = cur.fetchall()

    for r in rows:
        try:
            r["specs"] = json.loads(r["specs_json"]) if r.get("specs_json") else {}
        except Exception:
            r["specs"] = {}
        r.pop("specs_json", None)
        # Handle carousel images
        if r.get("carousel_images"):
            try:
                r["carousel_images"] = json.loads(r["carousel_images"]) if isinstance(r["carousel_images"], str) else r["carousel_images"]
            except:
                r["carousel_images"] = []
        else:
            r["carousel_images"] = []

    return rows

@app.get("/api/products/{pid}")
def api_product_detail(pid: str):
    p = get_product_by_id(pid)
    if not p:
        raise HTTPException(status_code=404, detail="product not found")
    return p

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    # ====== 内部函数：按订单号查订单 ======
    def get_order_by_no(order_no: str) -> Optional[Dict[str, Any]]:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id, order_no, status, receiver, phone_tail, total_amount, created_at "
                    "FROM orders WHERE order_no=%s",
                    (order_no,),
                )
                o = cur.fetchone()
                if not o:
                    return None
                cur.execute(
                    "SELECT product_id, shop_id, title, price, qty FROM order_items WHERE order_id=%s",
                    (o["id"],),
                )
                o["items"] = cur.fetchall()
        return o

    # 1) session
    sid = req.session_id or str(uuid.uuid4())
    if req.reset or sid not in SESSIONS:
        SESSIONS[sid] = []
    history = SESSIONS[sid]

    # 2) build llm + agent
    llm = AliyunQwenLLM(model_name=ALIYUN_MODEL_NAME, temperature=ALIYUN_TEMPERATURE)
    executor = build_agent(llm)

    # 3) run
    user_msg = req.message.strip()

    # ====== 店铺 persona ======
    system_prefix = ""
    if req.shop_id:
        shop = get_shop_by_id(req.shop_id)
        if shop and shop.get("persona"):
            system_prefix += (
                f"店铺名称：{shop.get('shop_name', '')}\n"
                f"客服风格要求：{shop['persona']}\n"
                f"退换政策：{shop.get('return_policy', '')}\n\n"
            )

    # ====== 商品上下文 ======
    product_ctx = ""
    if req.product_id:
        p = get_product_by_id(req.product_id)
        if p:
            product_ctx = (
                "当前咨询商品信息：\n"
                f"- 商品ID：{p['product_id']}\n"
                f"- 商品名：{p['title']}\n"
                f"- 类目：{p.get('category', '')}\n"
                f"- 价格：{p.get('price', '')}\n"
                f"- 参数：{json.dumps(p.get('specs', {}), ensure_ascii=False)}\n"
                f"- 介绍：{p.get('description', '')}\n\n"
            )

    # ====== 订单上下文（新增） ======
    order_ctx = ""
    if req.order_no:
        o = get_order_by_no(req.order_no)
        if o:
            created_at = o.get("created_at")
            if hasattr(created_at, "isoformat"):
                created_at = created_at.isoformat(sep=" ", timespec="seconds")

            order_ctx = (
                "当前咨询订单信息：\n"
                f"- 订单号：{o.get('order_no')}\n"
                f"- 状态：{o.get('status')}\n"
                f"- 金额：{o.get('total_amount')}\n"
                f"- 收件人：{o.get('receiver')}\n"
                f"- 手机尾号：{o.get('phone_tail')}\n"
                f"- 下单时间：{created_at}\n"
            )
            items = o.get("items") or []
            for idx, it in enumerate(items[:5], start=1):
                order_ctx += (
                    f"- 商品{idx}：{it.get('title')} x{it.get('qty')}（¥{it.get('price')}）"
                    f"店铺{it.get('shop_id')}\n"
                )
            order_ctx += "\n"
        else:
            order_ctx = (
                "当前咨询订单信息：\n"
                f"- 订单号：{req.order_no}\n"
                "- 说明：未在系统中找到该订单\n\n"
            )

    merged_user_msg = f"{system_prefix}{product_ctx}{order_ctx}用户问题：{user_msg}"

    history.append({"role": "user", "content": user_msg})

    answer, intermediate_steps = run_agent(executor, merged_user_msg, history)

    history.append({"role": "assistant", "content": answer})

    # 4) steps
    steps_out: List[StepItem] = []
    for action, obs in intermediate_steps:
        steps_out.append(StepItem(action=str(action), observation=str(obs)))

    return ChatResponse(session_id=sid, answer=answer, steps=steps_out)

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CreateOrderReq(BaseModel):
    product_id: str
    qty: int = 1
    receiver: Optional[str] = None
    phone_tail: Optional[str] = None

class CreateOrderResp(BaseModel):
    order_no: str
    status: str
    total_amount: float

def _gen_order_no() -> str:
    return datetime.now().strftime("%Y%m%d%H%M%S") + uuid.uuid4().hex[:6].upper()

def _get_product_snapshot(product_id: str) -> Dict[str, Any]:

    p = get_product_by_id(product_id)
    if not p:
        raise HTTPException(status_code=404, detail="product not found")
    return p

@app.post("/api/orders", response_model=CreateOrderResp)
def create_order(req: CreateOrderReq):
    if req.qty <= 0:
        raise HTTPException(status_code=400, detail="qty must be > 0")

    p = _get_product_snapshot(req.product_id)
    order_no = _gen_order_no()
    price = float(p.get("price", 0))
    total = price * req.qty
    
    # 获取商品图片URL：优先使用轮播图的第一张，否则使用 image_url
    image_url = ""
    carousel_images = p.get("carousel_images", [])
    if carousel_images and isinstance(carousel_images, list) and len(carousel_images) > 0:
        image_url = carousel_images[0]
    else:
        image_url = p.get("image_url", "")

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO orders(order_no, status, receiver, phone_tail, total_amount) VALUES(%s,%s,%s,%s,%s)",
                (order_no, "PAID", req.receiver, req.phone_tail, total),
            )
            order_id = cur.lastrowid
            cur.execute(
                "INSERT INTO order_items(order_id, product_id, shop_id, title, price, qty, image_url) VALUES(%s,%s,%s,%s,%s,%s,%s)",
                (order_id, p["product_id"], p["shop_id"], p["title"], price, req.qty, image_url),
            )

    return CreateOrderResp(order_no=order_no, status="PAID", total_amount=total)

@app.get("/api/orders")
def list_orders():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, order_no, status, receiver, phone_tail, total_amount, created_at "
                "FROM orders ORDER BY id DESC LIMIT 100"
            )
            orders = cur.fetchall()

            # 查每个订单的 items
            for o in orders:
                cur.execute(
                    "SELECT product_id, shop_id, title, price, qty, image_url FROM order_items WHERE order_id=%s",
                    (o["id"],),
                )
                o["items"] = cur.fetchall()
    return orders

@app.get("/api/orders/{order_no}")
def get_order(order_no: str):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, order_no, status, receiver, phone_tail, total_amount, created_at "
                "FROM orders WHERE order_no=%s",
                (order_no,),
            )
            o = cur.fetchone()
            if not o:
                raise HTTPException(status_code=404, detail="order not found")
            cur.execute(
                "SELECT product_id, shop_id, title, price, qty, image_url FROM order_items WHERE order_id=%s",
                (o["id"],),
            )
            o["items"] = cur.fetchall()
    return o

from pydantic import BaseModel
from typing import Optional
import uuid
from fastapi import HTTPException

class RefundReq(BaseModel):
    reason: Optional[str] = None

class RefundResp(BaseModel):
    after_sale_no: str
    status: str

def _gen_after_sale_no() -> str:
    return "AS" + uuid.uuid4().hex[:10].upper()

@app.post("/api/orders/{order_no}/refund", response_model=RefundResp)
def refund_order(order_no: str, req: RefundReq):
    # 1) 查订单是否存在
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT order_no, status FROM orders WHERE order_no=%s", (order_no,))
            o = cur.fetchone()
            if not o:
                raise HTTPException(status_code=404, detail="order not found")

            # 2) 简单规则：PAID 才允许退
            if o["status"] not in ("PAID", "SHIPPED", "DELIVERED"):
                raise HTTPException(status_code=400, detail=f"order status not refundable: {o['status']}")

            after_sale_no = _gen_after_sale_no()
            reason = (req.reason or "用户申请退货退款").strip()

            cur.execute(
                "INSERT INTO after_sales(after_sale_no, order_no, type, reason, status) VALUES(%s,%s,%s,%s,%s)",
                (after_sale_no, order_no, "REFUND", reason, "CREATED"),
            )

            # 3) 同步把订单状态改成 REFUNDING
            cur.execute("UPDATE orders SET status=%s WHERE order_no=%s", ("REFUNDING", order_no))

    return RefundResp(after_sale_no=after_sale_no, status="REFUNDING")


class AdminUpdateOrderReq(BaseModel):
    status: str

@app.patch("/api/admin/orders/{order_no}")
def admin_update_order(order_no: str, req: AdminUpdateOrderReq):
    allow = {"PAID", "SHIPPED", "DELIVERED", "CANCELLED", "REFUNDING", "REFUNDED"}
    if req.status not in allow:
        raise HTTPException(status_code=400, detail=f"invalid status, allow: {sorted(list(allow))}")

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE orders SET status=%s WHERE order_no=%s", (req.status, order_no))
            if cur.rowcount == 0:
                raise HTTPException(status_code=404, detail="order not found")
    return {"ok": True, "order_no": order_no, "status": req.status}

@app.delete("/api/orders/{order_no}")
def delete_order(order_no: str):
    with get_conn() as conn:
        with conn.cursor() as cur:
            # 1. 检查订单是否存在
            cur.execute("SELECT id FROM orders WHERE order_no=%s", (order_no,))
            o = cur.fetchone()
            if not o:
                raise HTTPException(status_code=404, detail="order not found")
            
            order_id = o["id"]
            
            # 2. 删除订单商品
            cur.execute("DELETE FROM order_items WHERE order_id=%s", (order_id,))
            
            # 3. 删除售后记录（如果有）
            cur.execute("DELETE FROM after_sales WHERE order_no=%s", (order_no,))
            
            # 4. 删除订单
            cur.execute("DELETE FROM orders WHERE id=%s", (order_id,))
            
    return {"ok": True, "order_no": order_no}

@app.delete("/api/admin/orders/{order_no}")
def admin_delete_order(order_no: str):
    with get_conn() as conn:
        with conn.cursor() as cur:
            # 1. 检查订单是否存在
            cur.execute("SELECT id FROM orders WHERE order_no=%s", (order_no,))
            o = cur.fetchone()
            if not o:
                raise HTTPException(status_code=404, detail="order not found")
            
            order_id = o["id"]
            
            # 2. 删除订单商品
            cur.execute("DELETE FROM order_items WHERE order_id=%s", (order_id,))
            
            # 3. 删除售后记录（如果有）
            cur.execute("DELETE FROM after_sales WHERE order_no=%s", (order_no,))
            
            # 4. 删除订单
            cur.execute("DELETE FROM orders WHERE id=%s", (order_id,))
            
    return {"ok": True, "order_no": order_no, "message": "订单已删除"}

import json as _json

def _db_product_to_dict(row: Dict[str, Any]) -> Dict[str, Any]:
    # specs_json 可能是 str / dict
    specs = row.get("specs_json")
    if isinstance(specs, str):
        try:
            specs = _json.loads(specs)
        except:
            specs = {}
    if specs is None:
        specs = {}
    row["specs"] = specs
    row.pop("specs_json", None)
    
    # Handle JSON fields
    if row.get("carousel_images"):
        try:
            row["carousel_images"] = json.loads(row["carousel_images"]) if isinstance(row["carousel_images"], str) else row["carousel_images"]
        except:
            row["carousel_images"] = []
    else:
        row["carousel_images"] = []
    
    if row.get("detail_images"):
        try:
            row["detail_images"] = json.loads(row["detail_images"]) if isinstance(row["detail_images"], str) else row["detail_images"]
        except:
            row["detail_images"] = []
    else:
        row["detail_images"] = []
    
    return row

@app.get("/api/products_db")
def api_products_db():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT product_id, shop_id, title, category, price, description, specs_json, image_url, carousel_images, detail_images, detailed_text, is_active "
                "FROM products ORDER BY id DESC LIMIT 200"
            )
            rows = cur.fetchall()
    return [_db_product_to_dict(r) for r in rows]

@app.post("/api/admin/upload")
async def admin_upload(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in [".jpg", ".jpeg", ".png", ".webp"]:
        raise HTTPException(status_code=400, detail="只允许 jpg/jpeg/png/webp")

    name = f"{uuid.uuid4().hex}{ext}"
    save_path = os.path.join(UPLOAD_DIR, name)

    content = await file.read()
    with open(save_path, "wb") as f:
        f.write(content)

    return {"url": f"/uploads/{name}"}

@app.post("/api/admin/products")
async def admin_create_product(
    product_id: str = Form(""),
    shop_id: str = Form(...),
    title: str = Form(...),
    category: str = Form(""),
    price: float = Form(0),
    description: str = Form(""),
    specs_json: str = Form("{}"),
    image_url: str = Form(""),
    carousel_images: str = Form("[]"),
    detailed_text: str = Form(""),
):
    if not product_id.strip():
        product_id = "P" + uuid.uuid4().hex[:8].upper()   # 自动生成 PXXXXXXXX

    try:
        _json.loads(specs_json or "{}")
    except:
        raise HTTPException(status_code=400, detail="specs_json 必须是合法JSON")
    
    # Validate JSON arrays
    try:
        carousel_images_list = json.loads(carousel_images)
        if not isinstance(carousel_images_list, list):
            raise HTTPException(status_code=400, detail="carousel_images 必须是JSON数组")
        # Limit to 5 images
        if len(carousel_images_list) > 5:
            raise HTTPException(status_code=400, detail="轮播图最多只能上传5张")
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="carousel_images 必须是合法JSON")

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO products(product_id, shop_id, title, category, price, description, specs_json, image_url, carousel_images, detailed_text) "
                "VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (product_id, shop_id, title, category, price, description, specs_json, image_url, carousel_images, detailed_text),
            )
    return {"ok": True, "product_id": product_id}

@app.put("/api/admin/products/{pid}")
async def admin_update_product(
    pid: str,
    title: str = Form(...),
    category: str = Form(""),
    price: float = Form(0),
    description: str = Form(""),
    specs_json: str = Form("{}"),
    image_url: str = Form(""),
    carousel_images: str = Form("[]"),
    detailed_text: str = Form(""),
):
    try:
        _json.loads(specs_json or "{}")
    except:
        raise HTTPException(status_code=400, detail="specs_json 必须是合法JSON")
    
    # Validate JSON arrays
    try:
        carousel_images_list = json.loads(carousel_images)
        if not isinstance(carousel_images_list, list):
            raise HTTPException(status_code=400, detail="carousel_images 必须是JSON数组")
        # Limit to 5 images
        if len(carousel_images_list) > 5:
            raise HTTPException(status_code=400, detail="轮播图最多只能上传5张")
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="carousel_images 必须是合法JSON")

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE products SET title=%s, category=%s, price=%s, description=%s, specs_json=%s, image_url=%s, carousel_images=%s, detailed_text=%s "
                "WHERE product_id=%s",
                (title, category, price, description, specs_json, image_url, carousel_images, detailed_text, pid),
            )
            if cur.rowcount == 0:
                raise HTTPException(status_code=404, detail="product not found")
    return {"ok": True}

@app.delete("/api/admin/products/{pid}")
def admin_delete_product(pid: str):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM products WHERE product_id=%s", (pid,))
            if cur.rowcount == 0:
                raise HTTPException(status_code=404, detail="product not found")
    return {"ok": True}

class AdminToggleReq(BaseModel):
    is_active: bool

@app.post("/api/admin/products/{product_id}/toggle")
def admin_toggle_product(product_id: str, req: AdminToggleReq):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE products SET is_active=%s WHERE product_id=%s",
                (1 if req.is_active else 0, product_id),
            )
            if cur.rowcount == 0:
                raise HTTPException(status_code=404, detail="product not found")
    return {"ok": True, "product_id": product_id, "is_active": req.is_active}



