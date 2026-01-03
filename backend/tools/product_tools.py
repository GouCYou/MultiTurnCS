# product_tools.py
"""商品相关的工具函数"""

from typing import Dict, List, Optional
from backend.database import get_conn
import json

def search_products_by_name(name: str, max_results: int = 5) -> Dict[str, any]:
    """根据商品名称模糊查询商品
    
    Args:
        name: 商品名称关键词，支持模糊匹配
        max_results: 返回的最大结果数
        
    Returns:
        包含查询结果的字典，格式如下：
        {
            "success": bool,
            "message": str,
            "products": List[Dict]
        }
    """
    if not name or not name.strip():
        return {
            "success": False,
            "message": "商品名称不能为空",
            "products": []
        }
    
    keyword = name.strip()
    
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                # 使用替换空格的方式进行模糊查询，支持空格不敏感的搜索
                # 例如：搜索"一加15"可以匹配"一加 15"、"一加   15"等
                cur.execute(
                    "SELECT product_id, shop_id, title, category, price, description, specs_json, image_url, carousel_images, is_active "
                    "FROM products WHERE is_active=1 AND REPLACE(title, ' ', '') LIKE REPLACE(%s, ' ', '') ORDER BY id DESC LIMIT %s",
                    (f"%{keyword}%", max_results)
                )
                rows = cur.fetchall()
        
        # 处理查询结果
        products = []
        for r in rows:
            product = {
                "product_id": r["product_id"],
                "shop_id": r["shop_id"],
                "title": r["title"],
                "category": r["category"],
                "price": float(r["price"]),
                "description": r["description"] or "",
                "image_url": r["image_url"] or "",
                "is_active": r["is_active"] == 1
            }
            
            # 处理 JSON 字段
            try:
                product["specs"] = json.loads(r["specs_json"]) if r.get("specs_json") else {}
            except Exception:
                product["specs"] = {}
            
            try:
                product["carousel_images"] = json.loads(r["carousel_images"]) if isinstance(r["carousel_images"], str) else r["carousel_images"]
            except Exception:
                product["carousel_images"] = []
            
            products.append(product)
        
        return {
            "success": True,
            "message": f"找到 {len(products)} 个相关商品",
            "products": products
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"查询商品时发生错误：{str(e)}",
            "products": []
        }

def get_product_detail(product_id: str) -> Dict[str, any]:
    """根据商品ID查询商品详情
    
    Args:
        product_id: 商品ID
        
    Returns:
        包含商品详情的字典，格式如下：
        {
            "success": bool,
            "message": str,
            "product": Dict
        }
    """
    if not product_id:
        return {
            "success": False,
            "message": "商品ID不能为空",
            "product": None
        }
    
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT product_id, shop_id, title, category, price, description, specs_json, image_url, carousel_images, detail_images, detailed_text, is_active "
                    "FROM products WHERE product_id=%s LIMIT 1",
                    (product_id,)
                )
                r = cur.fetchone()
        
        if not r:
            return {
                "success": False,
                "message": "未找到该商品",
                "product": None
            }
        
        product = {
            "product_id": r["product_id"],
            "shop_id": r["shop_id"],
            "title": r["title"],
            "category": r["category"],
            "price": float(r["price"]),
            "description": r["description"] or "",
            "image_url": r["image_url"] or "",
            "detailed_text": r["detailed_text"] or "",
            "is_active": r["is_active"] == 1
        }
        
        # 处理 JSON 字段
        try:
            product["specs"] = json.loads(r["specs_json"]) if r.get("specs_json") else {}
        except Exception:
            product["specs"] = {}
        
        try:
            product["carousel_images"] = json.loads(r["carousel_images"]) if isinstance(r["carousel_images"], str) else r["carousel_images"]
        except Exception:
            product["carousel_images"] = []
        
        try:
            product["detail_images"] = json.loads(r["detail_images"]) if isinstance(r["detail_images"], str) else r["detail_images"]
        except Exception:
            product["detail_images"] = []
        
        return {
            "success": True,
            "message": "查询成功",
            "product": product
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"查询商品详情时发生错误：{str(e)}",
            "product": None
        }
