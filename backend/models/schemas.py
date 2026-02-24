from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from bson import ObjectId

class PyObjectId(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return str(v)

# ── Shop Models ───────────────────────────────────────────────────────────────

class ShopCreate(BaseModel):
    name: str
    shop_type: str
    phone: str
    address: Optional[str] = ""
    owner_name: Optional[str] = ""
    email: Optional[str] = ""
    city: Optional[str] = ""
    whatsapp_number: Optional[str] = ""

class ShopUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    owner_name: Optional[str] = None
    email: Optional[str] = None
    city: Optional[str] = None
    whatsapp_number: Optional[str] = None

class ShopResponse(BaseModel):
    id: str
    name: str
    shop_type: str
    phone: str
    address: str
    owner_name: str
    email: str
    city: str
    whatsapp_number: str
    created_at: datetime
    template: dict

# ── Product Models ────────────────────────────────────────────────────────────

class ProductCreate(BaseModel):
    shop_id: str
    name: str
    price: float
    stock: int
    unit: Optional[str] = "piece"
    attributes: Optional[Dict[str, Any]] = {}
    description: Optional[str] = ""
    image_url: Optional[str] = ""
    low_stock_alert: Optional[int] = None
    active: Optional[bool] = True

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    unit: Optional[str] = None
    attributes: Optional[Dict[str, Any]] = None
    description: Optional[str] = None
    active: Optional[bool] = None
    low_stock_alert: Optional[int] = None

class ProductResponse(BaseModel):
    id: str
    shop_id: str
    name: str
    price: float
    stock: int
    unit: str
    attributes: Dict[str, Any]
    description: str
    active: bool
    low_stock_alert: int
    created_at: datetime
    updated_at: datetime

# ── Order Models ──────────────────────────────────────────────────────────────

class OrderItem(BaseModel):
    product_id: str
    product_name: str
    quantity: int
    unit_price: float
    total: float

class OrderCreate(BaseModel):
    shop_id: str
    customer_phone: Optional[str] = ""
    customer_name: Optional[str] = "Walk-in Customer"
    items: List[OrderItem]
    channel: Optional[str] = "manual"  # manual | whatsapp | app
    notes: Optional[str] = ""

class OrderStatus(BaseModel):
    status: str  # pending | confirmed | delivered | cancelled

class OrderResponse(BaseModel):
    id: str
    shop_id: str
    customer_phone: str
    customer_name: str
    items: List[OrderItem]
    total_amount: float
    status: str
    channel: str
    notes: str
    created_at: datetime

# ── WhatsApp / AI Models ──────────────────────────────────────────────────────

class WhatsAppMessage(BaseModel):
    shop_id: str
    customer_phone: str
    message: str
    customer_name: Optional[str] = ""

class ParsedOrderItem(BaseModel):
    name: str
    quantity: int
    matched_product_id: Optional[str] = None
    matched_product_name: Optional[str] = None
    unit_price: Optional[float] = None
    confidence: Optional[float] = 1.0

class ParsedOrder(BaseModel):
    items: List[ParsedOrderItem]
    raw_message: str
    parse_method: str  # rule_based | llm
