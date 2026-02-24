from fastapi import APIRouter, Query
from database.connection import get_db
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/dashboard")
async def dashboard_stats(shop_id: str = Query(...)):
    """Main dashboard stats — total products, orders, revenue, low stock count."""
    db = get_db()

    total_products = await db.products.count_documents({"shop_id": shop_id, "active": True})

    # Orders stats
    today = datetime.utcnow().replace(hour=0, minute=0, second=0)
    total_orders = await db.orders.count_documents({"shop_id": shop_id})
    today_orders = await db.orders.count_documents({
        "shop_id": shop_id,
        "created_at": {"$gte": today}
    })

    # Revenue
    pipeline = [
        {"$match": {"shop_id": shop_id}},
        {"$group": {"_id": None, "total": {"$sum": "$total_amount"}}}
    ]
    rev = await db.orders.aggregate(pipeline).to_list(1)
    total_revenue = rev[0]["total"] if rev else 0

    today_pipeline = [
        {"$match": {"shop_id": shop_id, "created_at": {"$gte": today}}},
        {"$group": {"_id": None, "total": {"$sum": "$total_amount"}}}
    ]
    today_rev = await db.orders.aggregate(today_pipeline).to_list(1)
    today_revenue = today_rev[0]["total"] if today_rev else 0

    # Low stock
    low_stock_pipeline = [
        {"$match": {"shop_id": shop_id, "active": True}},
        {"$addFields": {"is_low": {"$lte": ["$stock", "$low_stock_alert"]}}},
        {"$match": {"is_low": True}},
        {"$count": "count"}
    ]
    low_stock = await db.products.aggregate(low_stock_pipeline).to_list(1)
    low_stock_count = low_stock[0]["count"] if low_stock else 0

    # WhatsApp orders
    wa_orders = await db.orders.count_documents({"shop_id": shop_id, "channel": "whatsapp"})

    return {
        "total_products": total_products,
        "total_orders": total_orders,
        "today_orders": today_orders,
        "total_revenue": round(total_revenue, 2),
        "today_revenue": round(today_revenue, 2),
        "low_stock_count": low_stock_count,
        "whatsapp_orders": wa_orders,
    }

@router.get("/sales-chart")
async def sales_chart(shop_id: str = Query(...), days: int = Query(7)):
    """Daily sales data for the last N days."""
    db = get_db()
    start = datetime.utcnow() - timedelta(days=days)

    pipeline = [
        {"$match": {"shop_id": shop_id, "created_at": {"$gte": start}}},
        {"$group": {
            "_id": {
                "year": {"$year": "$created_at"},
                "month": {"$month": "$created_at"},
                "day": {"$dayOfMonth": "$created_at"},
            },
            "revenue": {"$sum": "$total_amount"},
            "orders": {"$sum": 1},
        }},
        {"$sort": {"_id.year": 1, "_id.month": 1, "_id.day": 1}},
    ]

    result = await db.orders.aggregate(pipeline).to_list(days)
    chart_data = []
    for r in result:
        d = r["_id"]
        chart_data.append({
            "date": f"{d['day']:02d}/{d['month']:02d}",
            "revenue": round(r["revenue"], 2),
            "orders": r["orders"],
        })
    return chart_data

@router.get("/top-products")
async def top_products(shop_id: str = Query(...), limit: int = Query(5)):
    """Top selling products by quantity."""
    db = get_db()
    pipeline = [
        {"$match": {"shop_id": shop_id}},
        {"$unwind": "$items"},
        {"$group": {
            "_id": "$items.product_name",
            "total_qty": {"$sum": "$items.quantity"},
            "total_revenue": {"$sum": "$items.total"},
        }},
        {"$sort": {"total_qty": -1}},
        {"$limit": limit},
    ]
    result = await db.orders.aggregate(pipeline).to_list(limit)
    return [{"name": r["_id"], "qty": r["total_qty"], "revenue": round(r["total_revenue"], 2)} for r in result]

@router.get("/channel-breakdown")
async def channel_breakdown(shop_id: str = Query(...)):
    """Orders broken down by channel (whatsapp vs manual vs app)."""
    db = get_db()
    pipeline = [
        {"$match": {"shop_id": shop_id}},
        {"$group": {"_id": "$channel", "count": {"$sum": 1}, "revenue": {"$sum": "$total_amount"}}},
    ]
    result = await db.orders.aggregate(pipeline).to_list(10)
    return [{"channel": r["_id"], "count": r["count"], "revenue": round(r["revenue"], 2)} for r in result]
