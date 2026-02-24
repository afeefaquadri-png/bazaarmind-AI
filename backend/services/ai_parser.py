"""
AI Order Parser: Converts natural language messages like "2 milk 1 bread"
into structured order data. Uses rule-based parsing first, LLM as fallback.
"""
import re
import os
import json
from typing import List
from database.connection import get_db
import google.generativeai as genai  # ✅ Gemini

# ✅ Gemini setup
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel("gemini-1.5-flash")
else:
    gemini_model = None


# 🔥 NEW: Multilingual synonyms (VERY IMPORTANT)
SYNONYMS = {
    "doodh": "milk",
    "milk": "milk",
    "anda": "eggs",
    "egg": "eggs",
    "eggs": "eggs",
    "bread": "bread",
    "double roti": "bread",
    "roti": "bread",
    "atta": "flour",
    "chawal": "rice",
    "paani": "water",
    "biscuit": "biscuits",
    "chips": "chips",
}


# Common quantity words
QUANTITY_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "ek": 1, "do": 2, "teen": 3, "char": 4, "paanch": 5,
    "half": 0.5, "dozen": 12, "couple": 2,
}


def parse_number(token: str) -> float | None:
    token_lower = token.lower()
    if token_lower in QUANTITY_WORDS:
        return QUANTITY_WORDS[token_lower]
    try:
        return float(token)
    except ValueError:
        return None


def rule_based_parse(message: str) -> List[dict]:
    msg = message.strip().lower()
    msg = re.sub(r'\b(and|aur|bhi|please|bhaiya|ji)\b', '', msg)
    msg = re.sub(r'[,;]+', ' ', msg)
    msg = re.sub(r'\s+', ' ', msg).strip()

    items = []
    tokens = msg.split()
    i = 0

    while i < len(tokens):
        qty = parse_number(tokens[i])
        if qty is not None and i + 1 < len(tokens):
            name_parts = []
            j = i + 1
            while j < len(tokens):
                if parse_number(tokens[j]) is not None:
                    if j + 1 < len(tokens) and parse_number(tokens[j + 1]) is None:
                        break
                name_parts.append(tokens[j])
                j += 1
            if name_parts:
                items.append({
                    "name": " ".join(name_parts),
                    "quantity": int(qty) if qty == int(qty) else qty,
                })
                i = j
            else:
                i += 1
        else:
            i += 1

    if not items:
        pattern = re.compile(r'([a-zA-Z\s]+?)\s+(\d+(?:\.\d+)?)')
        for match in pattern.finditer(msg):
            name = match.group(1).strip()
            qty = float(match.group(2))
            if name:
                items.append({
                    "name": name,
                    "quantity": int(qty) if qty == int(qty) else qty,
                })

    return items


async def match_products(parsed_items: List[dict], shop_id: str) -> List[dict]:
    db = get_db()
    products = await db.products.find({"shop_id": shop_id, "active": True}).to_list(500)

    matched = []
    for item in parsed_items:
        item_name = item["name"].lower()

        # 🔥 NEW: apply synonym normalization
        item_name = SYNONYMS.get(item_name, item_name)

        best_match = None
        best_score = 0

        for product in products:
            p_name = product["name"].lower()

            if item_name == p_name:
                best_match = product
                best_score = 1.0
                break

            if item_name in p_name or p_name in item_name:
                score = len(item_name) / max(len(p_name), len(item_name))
                if score > best_score:
                    best_score = score
                    best_match = product

            item_words = set(item_name.split())
            prod_words = set(p_name.split())
            overlap = len(item_words & prod_words)
            if overlap > 0:
                score = overlap / max(len(item_words), len(prod_words)) * 0.8
                if score > best_score:
                    best_score = score
                    best_match = product

        result = {
            "name": item["name"],
            "quantity": item["quantity"],
            "confidence": round(best_score, 2),
            "matched_product_id": None,
            "matched_product_name": None,
            "unit_price": None,
        }

        if best_match and best_score >= 0.4:
            result["matched_product_id"] = str(best_match["_id"])
            result["matched_product_name"] = best_match["name"]
            result["unit_price"] = best_match["price"]

        matched.append(result)

    return matched


# 🔥 UPGRADED Gemini parsing (VERY IMPORTANT)
async def llm_parse(message: str) -> List[dict]:
    if not gemini_model:
        return []

    prompt = f"""
You are an AI assistant for a small shop in India.

Understand ANY type of message:
- Hindi
- Hinglish
- English
- Mixed language
- Spelling mistakes
- Slang

Message:
"{message}"

Return ONLY JSON:
[{{"name": "milk", "quantity": 2}}]

Rules:
- "doodh" → milk
- "anda" → eggs
- "double roti" → bread
- Default quantity = 1
- Ignore words like "bhaiya", "please"
- If no items → return []
"""

    try:
        response = gemini_model.generate_content(prompt)
        text = response.text.strip() if response.text else ""

        text = text.replace("```json", "").replace("```", "").strip()

        return json.loads(text)

    except Exception as e:
        print(f"Gemini parse failed: {e}")
        return []


async def parse_order(message: str, shop_id: str) -> dict:
    parsed = rule_based_parse(message)
    method = "rule_based"

    # 🔥 IMPROVED fallback trigger
    if not parsed or len(parsed) == 0:
        parsed = await llm_parse(message)
        method = "llm"

    if parsed and shop_id:
        matched = await match_products(parsed, shop_id)
    else:
        matched = [{
            "name": p["name"],
            "quantity": p["quantity"],
            "confidence": 1.0,
            "matched_product_id": None,
            "matched_product_name": None,
            "unit_price": None
        } for p in parsed]

    return {
        "items": matched,
        "raw_message": message,
        "parse_method": method,
        "total_items": len(matched),
        "fully_matched": all(m["matched_product_id"] is not None for m in matched),
    }