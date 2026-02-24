from fastapi import APIRouter, HTTPException
from database.connection import get_db
from models.schemas import ShopCreate, ShopUpdate
from templates.shop_templates import get_template, get_all_shop_types, get_categories
from bson import ObjectId
from datetime import datetime

router = APIRouter()

def fix_id(doc):
    if doc and "_id" in doc:
        doc["id"] = str(doc.pop("_id"))
    return doc

@router.get("/types")
async def list_shop_types():
    return {"types": get_all_shop_types(), "categories": get_categories()}

@router.get("/types/{shop_type}/template")
async def get_shop_template(shop_type: str):
    return get_template(shop_type)

@router.post("/")
async def create_shop(shop: ShopCreate):
    db = get_db()
    template = get_template(shop.shop_type)
    doc = shop.dict()
    doc["created_at"] = datetime.utcnow()
    doc["updated_at"] = datetime.utcnow()
    doc["active"] = True
    doc["template"] = template
    try:
        result = await db.shops.insert_one(doc)
        created = await db.shops.find_one({"_id": result.inserted_id})
        return fix_id(created)
    except Exception as e:
        if "duplicate" in str(e).lower():
            raise HTTPException(400, "Phone number already registered")
        raise HTTPException(500, str(e))

@router.get("/")
async def list_shops():
    db = get_db()
    shops = await db.shops.find().to_list(100)
    return [fix_id(s) for s in shops]

@router.get("/{shop_id}")
async def get_shop(shop_id: str):
    db = get_db()
    shop = await db.shops.find_one({"_id": ObjectId(shop_id)})
    if not shop:
        raise HTTPException(404, "Shop not found")
    return fix_id(shop)

@router.put("/{shop_id}")
async def update_shop(shop_id: str, update: ShopUpdate):
    db = get_db()
    data = {k: v for k, v in update.dict().items() if v is not None}
    data["updated_at"] = datetime.utcnow()
    result = await db.shops.update_one({"_id": ObjectId(shop_id)}, {"$set": data})
    if result.matched_count == 0:
        raise HTTPException(404, "Shop not found")
    updated = await db.shops.find_one({"_id": ObjectId(shop_id)})
    return fix_id(updated)

@router.delete("/{shop_id}")
async def delete_shop(shop_id: str):
    db = get_db()
    result = await db.shops.delete_one({"_id": ObjectId(shop_id)})
    if result.deleted_count == 0:
        raise HTTPException(404, "Shop not found")
    return {"message": "Shop deleted"}
