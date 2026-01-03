# tools/order_tools.py
import os
import json
import time
import random
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from backend.database import get_conn

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
FAKE_DB_PATH = os.path.join(DATA_DIR, "fake_db.json")
AFTER_SALE_DB_PATH = os.path.join(DATA_DIR, "after_sale_db.json")
TICKET_DB_PATH = os.path.join(DATA_DIR, "ticket_db.json")


def _read_json(path: str, default):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _write_json(path: str, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _load_orders() -> List[Dict[str, Any]]:
    return _read_json(FAKE_DB_PATH, [])


def _find_order_by_id(order_id: str) -> Optional[Dict[str, Any]]:
    orders = _load_orders()
    for o in orders:
        if str(o.get("order_id", "")).strip().upper() == order_id.strip().upper():
            return o
    return None

def lookup_order(order_id: str, phone_tail: Optional[str] = None, receiver: Optional[str] = None) -> Dict[str, Any]:
    """
    MySQL版：根据订单号查询订单（order_id 就当作 order_no 使用）。
    phone_tail / receiver 传了就校验，不传不校验。
    返回：ok / message / order
    """
    order_no = (order_id or "").strip()
    if not order_no:
        return {"ok": False, "message": "缺少订单号，请先提供订单号（如 20251223xxxxxx）。", "order": None}

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, order_no, status, receiver, phone_tail, total_amount, created_at "
                "FROM orders WHERE order_no=%s",
                (order_no,),
            )
            o = cur.fetchone()

            if not o:
                return {"ok": False, "message": f"未找到订单 {order_no}", "order": None}

            # 身份校验（可选）
            if phone_tail and str(o.get("phone_tail") or "").strip() != str(phone_tail).strip():
                return {"ok": False, "message": "手机号尾号不匹配，无法查询该订单。", "order": None}
            if receiver and str(o.get("receiver") or "").strip() != str(receiver).strip():
                return {"ok": False, "message": "收件人姓名不匹配，无法查询该订单。", "order": None}

            # 订单明细
            cur.execute(
                "SELECT product_id, shop_id, title, price, qty FROM order_items WHERE order_id=%s",
                (o["id"],),
            )
            items = cur.fetchall()

    order = {
        "order_id": o["order_no"],
        "order_no": o["order_no"],
        "status": o["status"],
        "receiver": o.get("receiver"),
        "phone_tail": o.get("phone_tail"),
        "total_amount": float(o.get("total_amount") or 0),
        "created_at": str(o.get("created_at")),
        "items": items,
    }
    return {"ok": True, "message": "查询成功", "order": order}

def _get_order_from_mysql(order_no: str) -> Optional[Dict[str, Any]]:
    order_no = (order_no or "").strip()
    if not order_no:
        return None
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, order_no, status, receiver, phone_tail, total_amount, created_at "
                "FROM orders WHERE order_no=%s",
                (order_no,),
            )
            o = cur.fetchone()
            return o

# ========== 工具2：物流轨迹（完全模拟，不需要真实快递 API） ==========
def get_tracking(tracking_no: str) -> Dict[str, Any]:
    """
    根据运单号返回物流轨迹（模拟）。
    返回：carrier / tracking_no / status / traces[]
    """
    tracking_no = str(tracking_no).strip()
    if not tracking_no:
        return {"ok": False, "message": "运单号为空", "tracking": None}

    # 简单从前缀猜快递公司
    prefix = "".join([c for c in tracking_no[:4] if c.isalpha()]).upper()
    carrier_map = {
        "SF": "顺丰",
        "YT": "圆通",
        "YTO": "圆通",
        "ZTO": "中通",
        "STO": "申通",
        "JD": "京东物流",
        "EMS": "EMS",
        "ZT": "中通/自定义",
        "HTKY": "百世",
    }
    carrier = carrier_map.get(prefix, "快递公司")

    # 用运单号“伪随机”生成稳定轨迹（同一个 tracking_no 每次返回一致）
    seed = sum(ord(ch) for ch in tracking_no)
    rnd = random.Random(seed)

    cities = ["广州", "深圳", "上海", "北京", "杭州", "成都", "武汉", "南京", "西安", "重庆", "苏州", "长沙"]
    hubs = ["转运中心", "分拣中心", "集散中心", "仓库", "营业部"]
    steps = [
        "已揽收",
        "到达{}{}",
        "离开{}{}",
        "运输中（干线运输）",
        "到达{}{}",
        "派送中（快递员：{}）",
        "已签收（签收人：{}）"
    ]

    start = datetime.now() - timedelta(hours=rnd.randint(12, 120))
    traces = []
    courier_names = ["快递员", "快递员小王", "快递员阿强", "快递员小陈", "快递员小刘"]

    # 生成 5~7 条节点
    n = rnd.randint(5, 7)
    status = "运输中"
    for i in range(n):
        t = start + timedelta(hours=i * rnd.randint(3, 10))
        city = rnd.choice(cities)
        hub = rnd.choice(hubs)

        if i == 0:
            msg = "已揽收"
        elif i == n - 2:
            msg = f"派送中（快递员：{rnd.choice(courier_names)}）"
            status = "派送中"
        elif i == n - 1:
            # 50% 已签收，50% 仍派送中（更真实）
            if rnd.random() < 0.5:
                msg = f"已签收（签收人：{rnd.choice(['本人', '家人', '前台', '门卫'])}）"
                status = "已签收"
            else:
                msg = f"派送中（快递员：{rnd.choice(courier_names)}）"
                status = "派送中"
        else:
            # 中间节点
            template = rnd.choice(steps[1:5])
            if "{}{}" in template:
                msg = template.format(city, hub)
            else:
                msg = template

        traces.append({
            "time": t.strftime("%Y-%m-%d %H:%M"),
            "location": f"{city}{hub}",
            "status": msg
        })

    return {
        "ok": True,
        "message": "查询成功（模拟轨迹）",
        "tracking": {
            "carrier": carrier,
            "tracking_no": tracking_no,
            "status": status,
            "traces": traces
        }
    }


# ========== 工具3：退货资格判断（模拟规则） ==========
def check_return_eligibility(order_id: str) -> Dict[str, Any]:
    """
    MySQL版退货判断（简单但真实可用）：
    - PAID：允许申请（未发货阶段）
    - SHIPPED/DELIVERING：允许（拦截/拒收）
    - DELIVERED：7天内允许
    - REFUNDING/REFUNDED/CANCELED：不允许
    """
    o = _get_order_from_mysql(order_id)
    if not o:
        return {"ok": False, "eligible": False, "reason": f"未找到订单 {order_id}"}

    status = str(o.get("status") or "").upper()
    created_at = o.get("created_at")

    # 兼容 created_at 可能是 datetime 或 str
    if isinstance(created_at, str):
        try:
            created_dt = datetime.fromisoformat(created_at.replace("Z", ""))
        except Exception:
            created_dt = datetime.now()
    else:
        created_dt = created_at or datetime.now()

    days = (datetime.now() - created_dt).days

    if status in ["CANCELED", "REFUNDING", "REFUNDED"]:
        return {"ok": True, "eligible": False, "reason": f"订单状态为 {status}，不支持重复申请退货/退款。"}

    if status == "PAID":
        return {"ok": True, "eligible": True, "reason": "订单已支付未发货，可直接申请退款（模拟规则）。"}

    if status in ["SHIPPED", "DELIVERING"]:
        return {"ok": True, "eligible": True, "reason": "订单已发货/运输中，可申请拦截或拒收退回（模拟规则）。"}

    if status == "DELIVERED":
        if days <= 7:
            return {"ok": True, "eligible": True, "reason": f"已签收 {days} 天内，支持 7 天退货（模拟规则）。"}
        return {"ok": True, "eligible": False, "reason": f"已签收超过 7 天（{days} 天），不支持无理由退货（模拟规则）。"}

    # 兜底
    return {"ok": True, "eligible": True, "reason": "符合退货条件（默认规则）。"}

# ========== 工具4：创建售后单（模拟） ==========
def create_after_sale(order_id: str, after_sale_type: str = "退货退款", reason: str = "用户申请") -> Dict[str, Any]:
    """
    创建售后单（模拟），落盘到 data/after_sale_db.json
    """
    o = _find_order_by_id(order_id)
    if not o:
        return {"ok": False, "message": f"未找到订单 {order_id}", "after_sale": None}

    db = _read_json(AFTER_SALE_DB_PATH, [])
    after_sale_id = f"AS{int(time.time())}{random.randint(100,999)}"

    item = {
        "after_sale_id": after_sale_id,
        "order_id": order_id,
        "type": after_sale_type,
        "reason": reason,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "已创建",
        "next_step": "等待取件/寄回（模拟）"
    }
    db.append(item)
    _write_json(AFTER_SALE_DB_PATH, db)

    return {"ok": True, "message": "售后单已创建", "after_sale": item}


# ========== 工具5：创建工单（模拟升级/投诉） ==========
def create_ticket(ticket_type: str, detail: str, order_id: Optional[str] = None, priority: str = "P2") -> Dict[str, Any]:
    """
    创建工单（模拟），落盘到 data/ticket_db.json
    """
    db = _read_json(TICKET_DB_PATH, [])
    ticket_id = f"TK{int(time.time())}{random.randint(100,999)}"
    item = {
        "ticket_id": ticket_id,
        "type": ticket_type,
        "detail": detail,
        "order_id": order_id,
        "priority": priority,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "处理中"
    }
    db.append(item)
    _write_json(TICKET_DB_PATH, db)

    return {"ok": True, "message": "工单已创建（模拟）", "ticket": item}


# ========== 工具6：发放补偿券（模拟） ==========
def issue_coupon(receiver: str, amount: int = 10, reason: str = "体验补偿") -> Dict[str, Any]:
    """
    发放优惠券（模拟），不落盘也行（演示够用）
    """
    code = f"CP{random.randint(100000, 999999)}"
    return {
        "ok": True,
        "message": "已发放补偿券（模拟）",
        "coupon": {
            "code": code,
            "amount": amount,
            "receiver": receiver,
            "reason": reason,
            "valid_days": 30
        }
    }