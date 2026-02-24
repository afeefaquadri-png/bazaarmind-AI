from fastapi import APIRouter, HTTPException, Query
from database.connection import get_db
from models.schemas import OrderCreate, OrderStatus
from bson import ObjectId
from datetime import datetime

router = APIRouter()

def fix_id(doc):
    if doc and "_id" in doc:
        doc["id"] = str(doc.pop("_id"))
    return doc

@router.post("/")
async def create_order(order: OrderCreate):
    db = get_db()

    # Validate shop
    shop = await db.shops.find_one({"_id": ObjectId(order.shop_id)})
    if not shop:
        raise HTTPException(404, "Shop not found")

    # Validate stock for each item and build confirmed items
    confirmed_items = []
    total = 0.0

    for item in order.items:
        product = await db.products.find_one({"_id": ObjectId(item.product_id)})
        if not product:
            raise HTTPException(404, f"Product '{item.product_name}' not found")
        if product["stock"] < item.quantity:
            raise HTTPException(400, f"Insufficient stock for '{product['name']}'. Available: {product['stock']}")

        item_total = item.unit_price * item.quantity
        total += item_total
        confirmed_items.append({
            "product_id": item.product_id,
            "product_name": product["name"],
            "quantity": item.quantity,
            "unit_price": item.unit_price,
            "total": item_total,
        })

    # Deduct stock
    for item in order.items:
        await db.products.update_one(
            {"_id": ObjectId(item.product_id)},
            {"$inc": {"stock": -item.quantity}, "$set": {"updated_at": datetime.utcnow()}}
        )

    # Create order document
    doc = {
        "shop_id": order.shop_id,
        "customer_phone": order.customer_phone,
        "customer_name": order.customer_name,
        "items": confirmed_items,
        "total_amount": round(total, 2),
        "status": "confirmed",
        "channel": order.channel,
        "notes": order.notes,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }

    result = await db.orders.insert_one(doc)
    created = await db.orders.find_one({"_id": result.inserted_id})
    return fix_id(created)

@router.get("/")
async def list_orders(
    shop_id: str = Query(...),
    status: str = Query(None),
    channel: str = Query(None),
    limit: int = Query(50),
):
    db = get_db()
    query = {"shop_id": shop_id}
    if status:
        query["status"] = status
    if channel:
        query["channel"] = channel
    orders = await db.orders.find(query).sort("created_at", -1).limit(limit).to_list(limit)
    return [fix_id(o) for o in orders]

@router.get("/{order_id}")
async def get_order(order_id: str):
    db = get_db()
    order = await db.orders.find_one({"_id": ObjectId(order_id)})
    if not order:
        raise HTTPException(404, "Order not found")
    return fix_id(order)

@router.put("/{order_id}/status")
async def update_order_status(order_id: str, update: OrderStatus):
    db = get_db()
    valid = ["pending", "confirmed", "delivered", "cancelled"]
    if update.status not in valid:
        raise HTTPException(400, f"Invalid status. Must be one of: {valid}")
    result = await db.orders.update_one(
        {"_id": ObjectId(order_id)},
        {"$set": {"status": update.status, "updated_at": datetime.utcnow()}}
    )
    if result.matched_count == 0:
        raise HTTPException(404, "Order not found")
    updated = await db.orders.find_one({"_id": ObjectId(order_id)})
    return fix_id(updated)
