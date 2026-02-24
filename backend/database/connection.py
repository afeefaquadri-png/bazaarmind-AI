import motor.motor_asyncio
from pymongo import ASCENDING
import os

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "bazaarmind")

client = None
db = None

async def connect_db():
    global client, db
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    # Create indexes
    await db.shops.create_index([("phone", ASCENDING)], unique=True)
    await db.products.create_index([("shop_id", ASCENDING)])
    await db.orders.create_index([("shop_id", ASCENDING)])
    await db.orders.create_index([("created_at", ASCENDING)])
    print(f"✅ Connected to MongoDB: {DB_NAME}")

async def close_db():
    global client
    if client:
        client.close()
        print("MongoDB connection closed")

def get_db():
    return db
