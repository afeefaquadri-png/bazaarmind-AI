"""
AI Order Parser: Converts natural language messages like "2 milk 1 bread"
into structured order data. Uses rule-based parsing first, LLM as fallback.
Supports English, Hindi, and Hinglish with language-aware replies.
"""

import re
import os
import json
from typing import List
from database.connection import get_db
from google import genai

# ✅ Gemini setup
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)
else:
    client = None


# 🔥 Multilingual synonyms
SYNONYMS = {
    "doodh": "milk",
    "milk": "milk",
    "anda": "eggs",
    "ande": "eggs",
    "egg": "eggs",
    "eggs": "eggs",
    "bread": "bread",
    "double roti": "bread",
    "roti": "bread",
    "atta": "flour",
    "maida": "flour",
    "chawal": "rice",
    "chaawal": "rice",
    "paani": "water",
    "pani": "water",
    "biscuit": "biscuits",
    "biscuits": "biscuits",
    "chips": "chips",
    "namak": "salt",
    "salt": "salt",
    "dahi": "curd",
    "curd": "curd",
    "yogurt": "curd",
    "tel": "oil",
    "oil": "oil",
    "cheeni": "sugar",
    "chini": "sugar",
    "sugar": "sugar",
    "chai": "tea",
    "tea": "tea",
    "coffee": "coffee",
    "sabun": "soap",
    "soap": "soap",
    "butter": "butter",
    "makhan": "butter",
}

# 🔢 Quantity words
QUANTITY_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "ek": 1, "do": 2, "teen": 3, "char": 4, "paanch": 5,
    "chhe": 6, "saat": 7, "aath": 8, "nau": 9,
    "half": 0.5, "dozen": 12, "couple": 2,
}

# 🌐 Hindi/Hinglish indicator words — used for language detection
HINDI_WORDS = {
    "doodh", "anda", "ande", "roti", "chawal", "chaawal", "paani", "pani",
    "namak", "cheeni", "chini", "dahi", "tel", "atta", "maida", "chai",
    "sabun", "makhan", "aur", "bhi", "mujhe", "chahiye", "bhaiya", "bhai",
    "ji", "haan", "nahi", "ek", "do", "teen", "char", "paanch",
    "lana", "dena", "bhejo", "de", "kar",
}


def detect_language(message: str) -> str:
    """
    Returns 'hindi' if message is mostly Hindi/Hinglish,
    'english' if mostly English.
    """
    words = set(message.lower().split())
    hindi_count = len(words & HINDI_WORDS)
    # If 2+ Hindi words, treat as Hinglish/Hindi
    if hindi_count >= 2:
        return "hindi"
    # If any single strong Hindi word (like doodh, chawal), treat as Hindi
    if hindi_count == 1 and len(words) <= 5:
        return "hindi"
    return "english"


def parse_number(token: str) -> float | None:
    token_lower = token.lower()
    if token_lower in QUANTITY_WORDS:
        return QUANTITY_WORDS[token_lower]
    try:
        return float(token)
    except ValueError:
        return None


# ✅ Rule-based parser — handles "2 milk", "milk 2", bare words
def rule_based_parse(message: str) -> List[dict]:
    msg = message.strip().lower()

    # Remove filler words (Hindi + English)
    msg = re.sub(
        r'\b(and|aur|bhi|please|bhaiya|bhai|ji|mujhe|mjhe|chahiye|dena|de|do|bhejo|lana|laana|i|want|need|send|get|me|some|give)\b',
        '',
        msg
    )

    msg = re.sub(r'[,;]+', ' ', msg)
    msg = re.sub(r'\s+', ' ', msg).strip()

    items = []
    tokens = msg.split()
    i = 0

    while i < len(tokens):
        qty = parse_number(tokens[i])

        # Pattern: <number> <item_name(s)>
        if qty is not None and i + 1 < len(tokens):
            name_parts = []
            j = i + 1
            while j < len(tokens):
                if parse_number(tokens[j]) is not None:
                    break
                name_parts.append(tokens[j])
                j += 1

            if name_parts:
                items.append({
                    "name": " ".join(name_parts),
                    "quantity": int(qty) if qty == int(qty) else qty,
                })
                i = j
                continue

        # Pattern: <item_name> <number>  (e.g. "milk 2")
        if qty is None and i + 1 < len(tokens):
            next_qty = parse_number(tokens[i + 1])
            if next_qty is not None:
                items.append({
                    "name": tokens[i],
                    "quantity": int(next_qty) if next_qty == int(next_qty) else next_qty,
                })
                i += 2
                continue

        i += 1

    # 🔥 Fallback: bare known words with no quantity — assume qty 1
    if not items:
        for word in tokens:
            if word in SYNONYMS:
                items.append({
                    "name": word,
                    "quantity": 1
                })

    return items


# ✅ Product matching
async def match_products(parsed_items: List[dict], shop_id: str) -> List[dict]:
    db = get_db()
    products = await db.products.find(
        {"shop_id": shop_id, "active": True}
    ).to_list(500)

    matched = []

    for item in parsed_items:
        item_name = item["name"].lower()

        # 🔥 Synonym normalization
        for key, value in SYNONYMS.items():
            if key in item_name:
                item_name = value
                break

        # 🚫 Filter confusing products
        filtered_products = []
        for p in products:
            name = p["name"].lower()
            if item_name == "milk" and "chocolate" in name:
                continue
            filtered_products.append(p)

        best_match = None
        best_score = 0

        for product in filtered_products:
            p_name = product["name"].lower()

            # 🥇 Exact match
            if item_name == p_name:
                best_match = product
                best_score = 1.0
                break

            if item_name in p_name:
                score = 0.95
                if score > best_score:
                    best_score = score
                    best_match = product

            # Keyword match
            if any(word in p_name for word in item_name.split()):
                score = 0.7
                if item_name in p_name:
                    score += 0.2
                if score > best_score:
                    best_score = score
                    best_match = product

            # Overlap match
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

        if best_match and best_score >= 0.3:
            result["matched_product_id"] = str(best_match["_id"])
            result["matched_product_name"] = best_match["name"]
            result["unit_price"] = best_match["price"]

        matched.append(result)

    return matched


def _clean_json_response(text: str) -> str:
    """Strip markdown code fences and extra whitespace from LLM output."""
    text = text.strip()
    text = re.sub(r"^```(?:json)?", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(r"```$", "", text).strip()
    return text


# ✅ Gemini fallback parser — strict, no hallucination
async def llm_parse(message: str) -> List[dict]:
    if not client:
        return []

    prompt = f"""You are a grocery order parser for an Indian kirana shop.

Your ONLY job: extract item names and quantities from the customer's message.

Customer message: "{message}"

Rules:
- Output ONLY a valid JSON array. No explanation, no markdown, no code fences.
- Each object must have exactly two keys: "name" (string, in English) and "quantity" (number).
- "quantity" defaults to 1 if not mentioned.
- Translate Hindi/Urdu/Hinglish words to English grocery item names.
- If the message has no grocery items, output: []

Examples:
Input: "2 doodh aur ek bread chahiye"
Output: [{{"name": "milk", "quantity": 2}}, {{"name": "bread", "quantity": 1}}]

Input: "I need 3 eggs and some sugar"
Output: [{{"name": "eggs", "quantity": 3}}, {{"name": "sugar", "quantity": 1}}]

Input: "eggs do aur biscuit"
Output: [{{"name": "eggs", "quantity": 2}}, {{"name": "biscuits", "quantity": 1}}]

Input: "hello" or "ok" or "confirm"
Output: []

Now parse: "{message}"
Output:"""

    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt
        )

        text = response.text if response.text else ""
        text = _clean_json_response(text)

        if not text or text == "[]":
            return []

        parsed = json.loads(text)

        if not isinstance(parsed, list):
            return []

        valid = []
        for item in parsed:
            if isinstance(item, dict) and "name" in item and "quantity" in item:
                try:
                    valid.append({
                        "name": str(item["name"]).lower().strip(),
                        "quantity": float(item["quantity"]),
                    })
                except (ValueError, TypeError):
                    continue

        return valid

    except json.JSONDecodeError as e:
        print(f"[LLM Parse] JSON decode error: {e} | Raw: {text!r}")
        return []
    except Exception as e:
        print(f"[LLM Parse] Gemini error: {e}")
        return []


# ✅ MAIN FUNCTION
async def parse_order(message: str, shop_id: str) -> dict:
    parsed = rule_based_parse(message)

    if not parsed:
        parsed = await llm_parse(message)
        method = "llm"
    else:
        method = "rule_based"

    if parsed and shop_id:
        matched = await match_products(parsed, shop_id)
    else:
        matched = []

    return {
        "items": matched,
        "raw_message": message,
        "parse_method": method,
        "total_items": len(matched),
        "fully_matched": all(m["matched_product_id"] for m in matched),
    }


# ✅ CHAT REPLY — Language-aware: English message → English reply, Hindi → Hinglish reply
async def generate_chat_reply(message: str, order_data: dict) -> str:
    total = order_data.get("total", 0)
    items = order_data.get("items", [])
    shop_name = order_data.get("shop_name", "")

    lang = detect_language(message)

    # ── Fallback replies (no Gemini) ──────────────────────────────────────────
    if not client:
        if items:
            if lang == "english":
                return f"Got your order! Total is ₹{total:.0f}. Reply CONFIRM to place it 😊"
            else:
                return f"Ji! Order aa gaya. Total ₹{total:.0f} hai. CONFIRM bhejiye 😊"
        else:
            if lang == "english":
                return "What would you like to order? Please tell me the items! 😊"
            else:
                return "Kya chahiye bhaiya? Bata dijiye! 😊"

    # ── Build item summary for the prompt ─────────────────────────────────────
    if items:
        item_summary = "\n".join(
            f"- {i['product_name']} x{i['quantity']} = ₹{i['total']:.0f}"
            for i in items
        )
    else:
        item_summary = "No items matched in the shop catalog"

    # ── Language-specific persona and examples ────────────────────────────────
    if lang == "english":
        persona = "You are a friendly grocery shop assistant replying on WhatsApp."
        tone_rules = """Tone rules:
- Reply in clear, friendly English
- Sound warm and helpful, NOT robotic
- Do NOT repeat the full item list (a bill is sent separately)
- If items exist: briefly confirm the order and mention the total
- If no items: politely ask what they need
- Always end with: "Reply CONFIRM to place your order" (only when items exist)
- Use 1 emoji max"""
        examples = """Examples of good replies:
"Got it! Your order is ready. Total comes to ₹85. Reply CONFIRM to place your order 😊"
"Sure! I've noted your items — total is ₹120. Reply CONFIRM to confirm! 👍"
"Sorry, I didn't catch that. Could you tell me what you'd like to order? 😊" """
    else:
        persona = "You are a friendly Indian kirana shop owner (Bhaiya) replying on WhatsApp."
        tone_rules = """Tone rules:
- Reply in natural Hinglish (mix of Hindi and English)
- Sound warm and casual, like a real shopkeeper — NOT robotic
- Do NOT repeat the full item list (bill is sent separately)
- If items exist: briefly confirm and mention total
- If no items: politely ask to clarify
- Always end with: "CONFIRM reply karo order ke liye" (only when items exist)
- Use 1-2 emojis max"""
        examples = """Examples of good replies:
"Bilkul bhaiya! Order aa gaya. Total ₹85 ho gaya. CONFIRM reply karo 😊"
"Ji ji! Note kar liya. Total ₹120 hai. CONFIRM bhejiye! 👍"
"Kya chahiye bhaiya? Thoda clear batao, abhi pack karte hain 😊" """

    prompt = f"""{persona}

Customer's message: "{message}"
Shop: "{shop_name}"
Detected language: {"English" if lang == "english" else "Hindi/Hinglish"}
Items ordered:
{item_summary}
Order total: ₹{total:.0f}

Your task: Write a SHORT WhatsApp reply (2-3 lines max).

{tone_rules}

{examples}

Now write the reply:"""

    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt
        )

        text = response.text.strip() if response.text else ""

        if not text:
            # Fallback
            if items:
                if lang == "english":
                    return f"Got your order! Total is ₹{total:.0f}. Reply CONFIRM to place it 😊"
                else:
                    return f"Ji! Order aa gaya. Total ₹{total:.0f} hai. CONFIRM bhejiye 😊"
            else:
                if lang == "english":
                    return "What would you like to order? 😊"
                else:
                    return "Kya chahiye bhaiya? 😊"

        # Cap at 5 lines in case model is too verbose
        lines = text.strip().splitlines()
        return "\n".join(lines[:5])

    except Exception as e:
        print(f"[Chat Reply] Gemini error: {e}")
        if items:
            if lang == "english":
                return f"Order received! Total is ₹{total:.0f}. Reply CONFIRM to place it 😊"
            else:
                return f"Ji! Total ₹{total:.0f} hai. CONFIRM bhejiye 😊"
        return "What would you like to order? 😊" if lang == "english" else "Kya chahiye? 😊"
