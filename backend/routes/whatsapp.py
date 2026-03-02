from fastapi import APIRouter, Request, Query
from database.connection import get_db
from models.schemas import WhatsAppMessage
from services.ai_parser import parse_order, generate_chat_reply
from bson import ObjectId
from datetime import datetime
import os
import httpx

router = APIRouter()

TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_WHATSAPP = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")


# ✅ Send WhatsApp Message
async def send_whatsapp_reply(to: str, message: str):
    if not TWILIO_SID or not TWILIO_TOKEN:
        print(f"[WHATSAPP MOCK] To: {to}\nMessage: {message}")
        return {"status": "mock_sent"}

    url = f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_SID}/Messages.json"

    data = {
        "From": TWILIO_WHATSAPP,
        "To": f"whatsapp:{to}",
        "Body": message,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            data=data,
            auth=(TWILIO_SID, TWILIO_TOKEN)
        )

    return response.json()


# 🧾 BILL BUILDER — always included when there are matched items
def build_bill_message(shop_name: str, items: list, total: float) -> str:
    if not items:
        return ""

    lines = [f"🧾 *{shop_name} — Bill*\n"]

    for i, item in enumerate(items, start=1):
        name = item['product_name']
        qty = item['quantity']
        subtotal = item['total']
        lines.append(f"{i}. {name} x{qty}  →  ₹{subtotal:.0f}")

    lines.append("\n─────────────────────")
    lines.append(f"💰 *Total:  ₹{total:.0f}*")
    lines.append("─────────────────────")
    lines.append("\nReply *CONFIRM* to place your order ✅")

    return "\n".join(lines)


# ✅ Shared confirm detection — English + Hindi + Hinglish
def is_confirm_message(text: str) -> bool:
    clean = text.lower().strip()
    # Exact match words
    confirm_words = {
        "confirm", "yes", "ok", "okay", "sure", "yep", "yup",
        "haan", "ha", "han", "haa", "done", "y",
        "bilkul", "zaroor",
    }
    if clean in confirm_words:
        return True
    # Partial match phrases
    confirm_phrases = [
        "confirm", "place order", "kar do", "order karo",
        "ho jaye", "send it", "go ahead", "proceed",
    ]
    return any(phrase in clean for phrase in confirm_phrases)


@router.post("/webhook")
async def whatsapp_webhook(request: Request):
    db = get_db()
    form = await request.form()

    from_number = form.get("From", "").replace("whatsapp:", "")
    body = form.get("Body", "").strip()
    to_number = form.get("To", "").replace("whatsapp:", "")

    if not body:
        return {"status": "empty_message"}

    # 🧾 Store incoming message
    await db.whatsapp_messages.insert_one({
        "from": from_number,
        "to": to_number,
        "body": body,
        "direction": "inbound",
        "timestamp": datetime.utcnow(),
    })

    # 🏪 Find shop
    shop = await db.shops.find_one({"whatsapp_number": to_number})
    if not shop:
        shop = await db.shops.find_one({"phone": to_number})

    if not shop:
        await send_whatsapp_reply(from_number, "Shop not found. Please contact support.")
        return {"status": "shop_not_found"}

    shop_id = str(shop["_id"])
    shop_name = shop["name"]

    print(f"[WEBHOOK] From: {from_number} | Message: '{body}' | Is confirm: {is_confirm_message(body)}")

    # ✅ CONFIRM FLOW
    if is_confirm_message(body):
        session = await db.whatsapp_sessions.find_one(
            {
                "customer_phone": from_number,
                "shop_id": shop_id,
                "status": "pending"
            },
            sort=[("created_at", -1)]
        )

        if not session:
            await send_whatsapp_reply(
                from_number,
                "No pending order found. Please send your order first! 😊"
            )
            return {"status": "no_pending_order"}

        # 🧾 Create order in DB
        order_doc = {
            "shop_id": shop_id,
            "customer_phone": from_number,
            "customer_name": "WA Customer",
            "items": session["confirmed_items"],
            "total_amount": session["total"],
            "status": "confirmed",
            "channel": "whatsapp",
            "notes": f"Original message: {session['raw_message']}",
            "created_at": datetime.utcnow(),
        }
        await db.orders.insert_one(order_doc)

        # 📦 Update stock
        for item in session["confirmed_items"]:
            if item.get("product_id"):
                await db.products.update_one(
                    {"_id": ObjectId(item["product_id"])},
                    {
                        "$inc": {"stock": -item["quantity"]},
                        "$set": {"updated_at": datetime.utcnow()}
                    }
                )

        # 🔄 Mark session complete
        await db.whatsapp_sessions.update_one(
            {"_id": session["_id"]},
            {"$set": {"status": "completed"}}
        )

        reply = (
            f"🎉 *Order Confirmed!*\n"
            f"Thank you! Your order of ₹{session['total']:.0f} has been placed.\n"
            f"Shop: {shop_name} 😊"
        )
        await send_whatsapp_reply(from_number, reply)
        return {"status": "order_created"}

    # 🤖 PARSE ORDER
    parsed = await parse_order(body, shop_id)

    confirmed_items = []
    total = 0.0

    for item in parsed["items"]:
        if item["matched_product_id"]:
            amt = item["unit_price"] * item["quantity"]
            total += amt
            confirmed_items.append({
                "product_id": item["matched_product_id"],
                "product_name": item["matched_product_name"],
                "quantity": item["quantity"],
                "unit_price": item["unit_price"],
                "total": amt,
            })

    # 🔄 Reset previous sessions for this customer+shop
    await db.whatsapp_sessions.delete_many({
        "customer_phone": from_number,
        "shop_id": shop_id
    })

    # 💾 Save new pending session
    await db.whatsapp_sessions.insert_one({
        "customer_phone": from_number,
        "shop_id": shop_id,
        "raw_message": body,
        "parsed_items": parsed["items"],
        "confirmed_items": confirmed_items,
        "total": total,
        "status": "pending",
        "created_at": datetime.utcnow(),
    })

    # 🤖 Build reply = AI chat message + bill
    if confirmed_items:
        ai_text = await generate_chat_reply(body, {
            "items": confirmed_items,
            "total": total,
            "shop_name": shop_name,
        })
        bill = build_bill_message(shop_name, confirmed_items, total)
        # Always send both: friendly message + bill
        reply = f"{ai_text}\n\n{bill}"
    elif parsed["items"]:
        # Items were understood but none exist in this shop's catalog
        unmatched = ", ".join(i["name"] for i in parsed["items"])
        reply = (
            f"Sorry, '{unmatched}' is not available in our shop right now. "
            f"Please check our available items or try something else! 😊"
        )
    else:
        reply = await generate_chat_reply(body, {
            "items": [],
            "total": 0,
            "shop_name": shop_name,
        })

    await send_whatsapp_reply(from_number, reply)
    return {"status": "awaiting_confirmation", "parsed": parsed}


# ✅ Manual send
@router.post("/send")
async def send_message(msg: WhatsAppMessage):
    result = await send_whatsapp_reply(msg.customer_phone, msg.message)
    return {"status": "sent", "result": result}


# ✅ Parse API
@router.post("/parse-order")
async def parse_order_api(shop_id: str = Query(...), message: str = Query(...)):
    parsed = await parse_order(message, shop_id)
    return parsed


# ✅ Simulate — full flow: parse → session save → confirm → order create
@router.post("/simulate")
async def simulate_whatsapp(body: WhatsAppMessage):
    db = get_db()

    shop = await db.shops.find_one({"_id": ObjectId(body.shop_id)})
    shop_name = shop["name"] if shop else "Test Shop"
    shop_id = body.shop_id

    # Stable simulator identity per shop
    sim_phone = f"simulator_{shop_id}"

    print(f"[SIMULATE] Message: '{body.message}' | Is confirm: {is_confirm_message(body.message)}")

    # ✅ CONFIRM FLOW
    if is_confirm_message(body.message):
        session = await db.whatsapp_sessions.find_one(
            {
                "customer_phone": sim_phone,
                "shop_id": shop_id,
                "status": "pending"
            },
            sort=[("created_at", -1)]
        )

        if not session:
            return {
                "reply_preview": "No pending order found. Please send your order first! 😊",
                "status": "no_pending_order",
                "parsed": None,
            }

        # 🧾 Create order
        order_doc = {
            "shop_id": shop_id,
            "customer_phone": sim_phone,
            "customer_name": "Simulator Customer",
            "items": session["confirmed_items"],
            "total_amount": session["total"],
            "status": "confirmed",
            "channel": "simulator",
            "notes": f"Original message: {session['raw_message']}",
            "created_at": datetime.utcnow(),
        }
        await db.orders.insert_one(order_doc)

        # 📦 Update stock
        for item in session["confirmed_items"]:
            if item.get("product_id"):
                await db.products.update_one(
                    {"_id": ObjectId(item["product_id"])},
                    {
                        "$inc": {"stock": -item["quantity"]},
                        "$set": {"updated_at": datetime.utcnow()}
                    }
                )

        # 🔄 Mark complete
        await db.whatsapp_sessions.update_one(
            {"_id": session["_id"]},
            {"$set": {"status": "completed"}}
        )

        reply = (
            f"🎉 *Order Confirmed!*\n"
            f"Thank you! Your order of ₹{session['total']:.0f} has been placed.\n"
            f"Shop: {shop_name} 😊"
        )

        return {
            "reply_preview": reply,
            "status": "order_created",
            "parsed": None,
            "order_total": session["total"],
            "confirmed_items": session["confirmed_items"],
        }

    # 🤖 PARSE ORDER
    parsed = await parse_order(body.message, shop_id)

    confirmed_items = []
    total = 0.0

    for item in parsed["items"]:
        if item["matched_product_id"]:
            amt = item["unit_price"] * item["quantity"]
            total += amt
            confirmed_items.append({
                "product_id": item["matched_product_id"],
                "product_name": item["matched_product_name"],
                "quantity": item["quantity"],
                "unit_price": item["unit_price"],
                "total": amt,
            })

    # 🔄 Reset old simulator session
    await db.whatsapp_sessions.delete_many({
        "customer_phone": sim_phone,
        "shop_id": shop_id
    })

    # 💾 Save session so CONFIRM works on next message
    await db.whatsapp_sessions.insert_one({
        "customer_phone": sim_phone,
        "shop_id": shop_id,
        "raw_message": body.message,
        "parsed_items": parsed["items"],
        "confirmed_items": confirmed_items,
        "total": total,
        "status": "pending",
        "created_at": datetime.utcnow(),
    })

    # 🤖 Build reply
    if confirmed_items:
        ai_text = await generate_chat_reply(body.message, {
            "items": confirmed_items,
            "total": total,
            "shop_name": shop_name,
        })
        bill = build_bill_message(shop_name, confirmed_items, total)
        reply = f"{ai_text}\n\n{bill}"
    elif parsed["items"]:
        unmatched = ", ".join(i["name"] for i in parsed["items"])
        reply = (
            f"Sorry, '{unmatched}' is not available in our shop right now. "
            f"Please check available items or try something else! 😊"
        )
    else:
        reply = await generate_chat_reply(body.message, {
            "items": [],
            "total": 0,
            "shop_name": shop_name,
        })

    return {
        "parsed": parsed,
        "reply_preview": reply,
        "status": "awaiting_confirmation",
        "confirmed_items": confirmed_items,
        "total": total,
    }

