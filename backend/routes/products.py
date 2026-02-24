from fastapi import APIRouter, HTTPException, Query
from database.connection import get_db
from models.schemas import ProductCreate, ProductUpdate
from templates.shop_templates import get_template
from bson import ObjectId
from datetime import datetime

router = APIRouter()

def fix_id(doc):
    if doc and "_id" in doc:
        doc["id"] = str(doc.pop("_id"))
    return doc

@router.post("/")
async def create_product(product: ProductCreate):
    db = get_db()
    # Validate shop exists
    shop = await db.shops.find_one({"_id": ObjectId(product.shop_id)})
    if not shop:
        raise HTTPException(404, "Shop not found")

    # Get template and set default low_stock_alert
    template = get_template(shop["shop_type"])
    low_stock = product.low_stock_alert or template.get("low_stock_threshold", 5)

    doc = product.dict()
    doc["shop_type"] = shop["shop_type"]
    doc["low_stock_alert"] = low_stock
    doc["created_at"] = datetime.utcnow()
    doc["updated_at"] = datetime.utcnow()

    result = await db.products.insert_one(doc)
    created = await db.products.find_one({"_id": result.inserted_id})
    return fix_id(created)

@router.get("/")
async def list_products(
    shop_id: str = Query(..., description="Shop ID"),
    active_only: bool = Query(False),
    low_stock: bool = Query(False),
):
    db = get_db()
    query = {"shop_id": shop_id}
    if active_only:
        query["active"] = True
    if low_stock:
        # Products where stock <= low_stock_alert
        query["$expr"] = {"$lte": ["$stock", "$low_stock_alert"]}
    products = await db.products.find(query).to_list(500)
    return [fix_id(p) for p in products]

@router.get("/low-stock")
async def low_stock_products(shop_id: str = Query(...)):
    db = get_db()
    # Find products where current stock <= alert threshold
    pipeline = [
        {"$match": {"shop_id": shop_id}},
        {"$addFields": {"is_low": {"$lte": ["$stock", "$low_stock_alert"]}}},
        {"$match": {"is_low": True}},
    ]
    products = await db.products.aggregate(pipeline).to_list(100)
    return [fix_id(p) for p in products]

@router.get("/{product_id}")
async def get_product(product_id: str):
    db = get_db()
    product = await db.products.find_one({"_id": ObjectId(product_id)})
    if not product:
        raise HTTPException(404, "Product not found")
    return fix_id(product)

@router.put("/{product_id}")
async def update_product(product_id: str, update: ProductUpdate):
    db = get_db()
    data = {k: v for k, v in update.dict().items() if v is not None}
    data["updated_at"] = datetime.utcnow()
    result = await db.products.update_one({"_id": ObjectId(product_id)}, {"$set": data})
    if result.matched_count == 0:
        raise HTTPException(404, "Product not found")
    updated = await db.products.find_one({"_id": ObjectId(product_id)})
    return fix_id(updated)

@router.delete("/{product_id}")
async def delete_product(product_id: str):
    db = get_db()
    result = await db.products.delete_one({"_id": ObjectId(product_id)})
    if result.deleted_count == 0:
        raise HTTPException(404, "Product not found")
    return {"message": "Product deleted"}

@router.post("/{product_id}/adjust-stock")
async def adjust_stock(product_id: str, adjustment: int):
    """Add or subtract stock. Use negative for reduction."""
    db = get_db()
    product = await db.products.find_one({"_id": ObjectId(product_id)})
    if not product:
        raise HTTPException(404, "Product not found")
    new_stock = product["stock"] + adjustment
    if new_stock < 0:
        raise HTTPException(400, f"Insufficient stock. Current: {product['stock']}")
    await db.products.update_one(
        {"_id": ObjectId(product_id)},
        {"$set": {"stock": new_stock, "updated_at": datetime.utcnow()}}
    )
    return {"product_id": product_id, "old_stock": product["stock"], "new_stock": new_stock}
