from fastapi import APIRouter, Request, HTTPException, Query
from database.connection import get_db
from models.schemas import WhatsAppMessage
from services.ai_parser import parse_order
from bson import ObjectId
from datetime import datetime
import os
import httpx
import google.generativeai as genai  # ✅ Gemini

router = APIRouter()

TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_WHATSAPP = os.getenv("TWILIO_WHATSAPP_NUMBER", "whatsapp:+14155238886")

# ✅ Gemini initialization
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel("gemini-1.5-flash-latest")
else:
    gemini_model = None


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

    async with httpx.AsyncClient() as client_http:
        response = await client_http.post(
            url,
            data=data,
            auth=(TWILIO_SID, TWILIO_TOKEN)
        )

    return response.json()


def build_confirmation_message(parsed: dict, shop_name: str) -> str:
    if not parsed["items"]:
        return f"Hi! We couldn't understand your order. Please try:\n'2 milk 1 bread'\n\nShop: {shop_name}"

    lines = [f"🛒 *{shop_name}* — Order Summary\n"]
    total = 0.0
    missing = []

    for item in parsed["items"]:
        if item["matched_product_id"]:
            price = item["unit_price"] * item["quantity"]
            total += price
            lines.append(f"✅ {item['quantity']}x {item['matched_product_name']} — Rs.{price:.0f}")
        else:
            missing.append(item["name"])
            lines.append(f"❓ {item['quantity']}x {item['name']} — *not found*")

    lines.append(f"\n💰 *Total: Rs.{total:.2f}*")

    if missing:
        lines.append(f"\n⚠️ Items not found: {', '.join(missing)}")
        lines.append("Please check spelling or ask the shopkeeper.")

    if all(i["matched_product_id"] for i in parsed["items"]):
        lines.append("\n✅ Reply *CONFIRM* to place your order")
    else:
        lines.append("\nReply *CONFIRM* to place available items only")

    return "\n".join(lines)


@router.post("/webhook")
async def whatsapp_webhook(request: Request):
    db = get_db()
    form = await request.form()

    from_number = form.get("From", "").replace("whatsapp:", "")
    body = form.get("Body", "").strip()
    to_number = form.get("To", "").replace("whatsapp:", "")

    if not body:
        return {"status": "empty_message"}

    # ✅ Log message
    await db.whatsapp_messages.insert_one({
        "from": from_number,
        "to": to_number,
        "body": body,
        "direction": "inbound",
        "timestamp": datetime.utcnow(),
    })

    # ✅ Find shop
    shop = await db.shops.find_one({"whatsapp_number": to_number})
    if not shop:
        shop = await db.shops.find_one({"phone": to_number})

    if not shop:
        await send_whatsapp_reply(from_number, "Shop not found. Please contact support.")
        return {"status": "shop_not_found"}

    shop_id = str(shop["_id"])
    shop_name = shop["name"]

    # 🔥 SMART CONFIRM (FIXED + IMPROVED)
    confirm_words = ["confirm", "yes", "ok", "okay", "haan", "ha", "han", "kar do", "place order", "done"]

    if any(word in body.lower() for word in confirm_words):
        session = await db.whatsapp_sessions.find_one({
            "customer_phone": from_number,
            "shop_id": shop_id,
            "status": "pending"
        }, sort=[("created_at", -1)])

        if not session:
            await send_whatsapp_reply(from_number, "No pending order found. Send your order first!")
            return {"status": "no_pending_order"}

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

        # Update stock
        for item in session["confirmed_items"]:
            if item.get("product_id"):
                await db.products.update_one(
                    {"_id": ObjectId(item["product_id"])},
                    {
                        "$inc": {"stock": -item["quantity"]},
                        "$set": {"updated_at": datetime.utcnow()}
                    }
                )

        await db.whatsapp_sessions.update_one(
            {"_id": session["_id"]},
            {"$set": {"status": "completed"}}
        )

        reply = f"🎉 *Order Confirmed!*\nThank you! Your order of Rs.{session['total']:.2f} has been placed.\n\nShop: {shop_name}"
        await send_whatsapp_reply(from_number, reply)

        return {"status": "order_created"}

    # 🤖 Gemini AI reply
    ai_reply = None
    if gemini_model:
        try:
            prompt = f"""
You are a smart shop assistant in India.

Understand Hindi, Hinglish, and English.

Customer message:
{body}

If it's an order → understand items.
If it's casual → reply naturally.
"""
            response = gemini_model.generate_content(prompt)
            ai_reply = response.text.strip() if response.text else None
        except Exception as e:
            print("Gemini AI error:", e)

    # ✅ Parse order
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

    # ✅ Store session
    await db.whatsapp_sessions.delete_many({
        "customer_phone": from_number,
        "shop_id": shop_id
    })

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

    # ✅ Reply
    reply = build_confirmation_message(parsed, shop_name)

    if not parsed["items"] and ai_reply:
        reply = ai_reply

    await send_whatsapp_reply(from_number, reply)

    return {"status": "awaiting_confirmation", "parsed": parsed}


@router.post("/send")
async def send_message(msg: WhatsAppMessage):
    result = await send_whatsapp_reply(msg.customer_phone, msg.message)
    return {"status": "sent", "result": result}


@router.post("/parse-order")
async def parse_order_api(shop_id: str = Query(...), message: str = Query(...)):
    parsed = await parse_order(message, shop_id)
    return parsed


@router.post("/simulate")
async def simulate_whatsapp(body: WhatsAppMessage):
    db = get_db()

    shop = await db.shops.find_one({"_id": ObjectId(body.shop_id)})
    shop_name = shop["name"] if shop else "Test Shop"

   # 🔥 CONFIRM LOGIC
    confirm_words = ["confirm", "yes", "ok", "okay", "haan", "ha", "han", "kar do", "place order", "done"]

    if any(word in body.message.lower() for word in confirm_words):
        session = await db.whatsapp_sessions.find_one({
            "customer_phone": body.customer_phone,
            "shop_id": body.shop_id,
            "status": "pending"
        }, sort=[("created_at", -1)])

        print("SESSION:", session)

        if not session or not session.get("confirmed_items"):
            return {
                "reply_preview": "No valid items to order.",
                "status": "no_items"
           }

        # ✅ CREATE ORDER (THIS WAS MISSING)
        order_doc = {
            "shop_id": body.shop_id,
            "customer_phone": body.customer_phone,
            "customer_name": "WA Customer",
            "items": session["confirmed_items"],
            "total_amount": session["total"],
            "status": "confirmed",
            "channel": "whatsapp",
            "notes": f"Original message: {session['raw_message']}",
            "created_at": datetime.utcnow(),
       }

        result = await db.orders.insert_one(order_doc)

        print("ORDER CREATED:", result.inserted_id)
        # ✅ STOCK UPDATE
        for item in session["confirmed_items"]:
            if item.get("product_id"):
                await db.products.update_one(
                    {"_id": ObjectId(item["product_id"])},
                    {
                        "$inc": {"stock": -item["quantity"]},
                        "$set": {"updated_at": datetime.utcnow()}
                   }
            )
        # ✅ UPDATE SESSION
        await db.whatsapp_sessions.update_one(
            {"_id": session["_id"]},
            {"$set": {"status": "completed"}}
        )

        return {
            "reply_preview": f"🎉 Order Confirmed! Total: Rs.{session['total']:.2f}",
            "status": "order_created"
       }

    # ✅ Parse
    parsed = await parse_order(body.message, body.shop_id)

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

    # 🔥 SAVE SESSION (this was missing)
    await db.whatsapp_sessions.delete_many({
        "customer_phone": body.customer_phone,
        "shop_id": body.shop_id
    })

    await db.whatsapp_sessions.insert_one({
        "customer_phone": body.customer_phone,
        "shop_id": body.shop_id,
        "raw_message": body.message,
        "parsed_items": parsed["items"],
        "confirmed_items": confirmed_items,
        "total": total,
        "status": "pending",
        "created_at": datetime.utcnow(),
    })

    reply = build_confirmation_message(parsed, shop_name)

    return {
        "parsed": parsed,
        "reply_preview": reply,
        "status": "simulated",
    }