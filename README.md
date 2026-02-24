# BazaarMind AI — Production-Ready MVP

> AI-powered Business Operating System for Indian Small Retail

---

## 📁 Project Structure

```
bazaarmind/
├── backend/
│   ├── main.py                    # FastAPI app entry point
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── .env.example
│   ├── database/
│   │   └── connection.py          # MongoDB async connection + indexes
│   ├── models/
│   │   └── schemas.py             # All Pydantic models
│   ├── routes/
│   │   ├── shops.py               # Shop CRUD + type listing
│   │   ├── products.py            # Product CRUD with dynamic attrs
│   │   ├── orders.py              # Order creation + stock deduction
│   │   ├── whatsapp.py            # Webhook + simulator + send
│   │   └── analytics.py          # Dashboard stats + chart data
│   ├── services/
│   │   └── ai_parser.py          # Rule-based + LLM order parsing
│   └── templates/
│       └── shop_templates.py     # 20+ shop type configs (THE CORE)
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx                # Router
│   │   ├── main.jsx               # Entry point
│   │   ├── index.css              # Tailwind + custom styles
│   │   ├── components/
│   │   │   ├── Layout.jsx         # Sidebar + shop switcher
│   │   │   ├── Modal.jsx          # Reusable modal
│   │   │   └── DynamicProductForm.jsx  # ⭐ Dynamic form engine
│   │   ├── hooks/
│   │   │   └── useShop.jsx        # Global shop context
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx      # Stats + charts
│   │   │   ├── Products.jsx       # Product management
│   │   │   ├── Orders.jsx         # Order management
│   │   │   ├── Shops.jsx          # Shop creation + selection
│   │   │   └── WhatsApp.jsx       # Bot simulator
│   │   └── services/
│   │       └── api.js             # All API calls (clean layer)
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── Dockerfile
│
├── docker-compose.yml
├── start.sh
└── README.md
```

---

## ⚡ Quick Start (Local Dev)

### Prerequisites
- Python 3.11+
- Node.js 18+
- MongoDB running locally

### Option 1: One-command start
```bash
chmod +x start.sh
./start.sh
```

### Option 2: Manual

**Backend:**
```bash
cd backend
cp .env.example .env       # Edit with your keys
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

**Access:**
- Dashboard: http://localhost:3000
- API Docs: http://localhost:8000/docs

### Option 3: Docker Compose
```bash
docker-compose up --build
```

---

## 🧠 Core Architecture Decisions

### 1. Multi-Shop Type System (Dynamic Attributes)

The entire system adapts to any shop type through a single `shop_templates.py` config:

```python
SHOP_TEMPLATES = {
    "kirana": {
        "attributes": [
            {"key": "expiry_date", "label": "Expiry Date", "type": "date", "required": True},
            {"key": "weight",      "label": "Weight",      "type": "text", "required": False},
        ],
        ...
    },
    "clothing": {
        "attributes": [
            {"key": "size",  "label": "Size",  "type": "select", "options": ["S","M","L","XL"]},
            {"key": "color", "label": "Color", "type": "text"},
        ],
        ...
    }
}
```

**To add a new shop type:** Just add an entry to `SHOP_TEMPLATES`. No other code changes needed.

### 2. Single Products Collection

ALL shop types share one MongoDB collection:
```json
{
  "name": "Amul Milk",
  "price": 28,
  "stock": 50,
  "shop_id": "abc123",
  "shop_type": "kirana",
  "attributes": {
    "expiry_date": "2025-03-15",
    "weight": "500ml",
    "brand": "Amul"
  }
}
```

### 3. Dynamic Frontend Form

`DynamicProductForm.jsx` reads the shop's template and auto-renders:
- text inputs
- number inputs
- date pickers
- select dropdowns

No hardcoded UI per shop type.

### 4. AI Order Parsing Pipeline

```
"2 milk 1 bread"
       ↓
Rule-based regex parser (fast, no API cost)
       ↓ (if fails)
LLM parser (OpenAI/Claude)
       ↓
Fuzzy product matching against shop inventory
       ↓
{ items: [{name, qty, product_id, unit_price, confidence}] }
```

---

## 🔌 API Reference

### Shops
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/shops/types` | All shop types + categories |
| GET | `/api/shops/types/{type}/template` | Template for a shop type |
| POST | `/api/shops/` | Create shop |
| GET | `/api/shops/` | List all shops |
| PUT | `/api/shops/{id}` | Update shop |
| DELETE | `/api/shops/{id}` | Delete shop |

### Products
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/products/` | Create product |
| GET | `/api/products/?shop_id={id}` | List products |
| GET | `/api/products/low-stock?shop_id={id}` | Low stock items |
| PUT | `/api/products/{id}` | Update product |
| DELETE | `/api/products/{id}` | Delete product |
| POST | `/api/products/{id}/adjust-stock?adjustment=N` | Adjust stock |

### Orders
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/orders/` | Create order (auto-deducts stock) |
| GET | `/api/orders/?shop_id={id}` | List orders |
| PUT | `/api/orders/{id}/status` | Update status |

### WhatsApp
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/whatsapp/webhook` | Twilio webhook (real WhatsApp) |
| POST | `/api/whatsapp/simulate` | Simulate (no Twilio needed) |
| POST | `/api/whatsapp/parse-order?shop_id=&message=` | Just parse, no reply |

### Analytics
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/analytics/dashboard?shop_id={id}` | Summary stats |
| GET | `/api/analytics/sales-chart?shop_id={id}&days=7` | Daily sales |
| GET | `/api/analytics/top-products?shop_id={id}` | Best sellers |
| GET | `/api/analytics/channel-breakdown?shop_id={id}` | WhatsApp vs manual |

---

## 💬 WhatsApp Integration

### Option A: Twilio (easiest)
1. Create Twilio account, get WhatsApp sandbox number
2. Add to `.env`:
   ```
   TWILIO_ACCOUNT_SID=AC...
   TWILIO_AUTH_TOKEN=...
   TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
   ```
3. Set webhook URL in Twilio: `https://yourdomain.com/api/whatsapp/webhook`
4. Use ngrok for local testing: `ngrok http 8000`

### Option B: Meta Business API (production)
1. Apply for WhatsApp Business API access
2. Create webhook pointing to `/api/whatsapp/webhook`
3. Update `send_whatsapp_reply()` in `routes/whatsapp.py` for Meta format

### Option C: Simulator (for testing, no Twilio needed)
Use the built-in simulator at http://localhost:3000/whatsapp

---

## 🤖 AI Integration

### With OpenAI:
```env
OPENAI_API_KEY=sk-...
```

### With Anthropic Claude:
```env
ANTHROPIC_API_KEY=sk-ant-...
```

The parser auto-detects which key is available. If neither, it uses rule-based parsing only (works well for standard orders).

---

## 🛒 Supported Shop Types (20+)

| Category | Types |
|----------|-------|
| Retail | kirana, supermarket, general_store |
| Fashion | clothing, footwear, boutique |
| Automotive | auto_parts, bike_repair, car_service |
| Food | restaurant, street_food, bakery, cafe |
| Health | pharmacy, medical_store |
| Home | hardware_store, electrical_shop, furniture_store |
| Electronics | mobile_shop, electronics_store |
| Others | stationery, gift_shop, cosmetics |

**To add more:** Edit `backend/templates/shop_templates.py` only.

---

## 🔧 Environment Variables

```env
# Required
MONGO_URL=mongodb://localhost:27017
DB_NAME=bazaarmind

# WhatsApp (optional for testing, use simulator otherwise)
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886

# AI parsing (optional, rule-based works without)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

---

## 🚀 What to Build Next

### Phase 2 (Month 5-9)
- [ ] Voice order processing (Whisper STT)
- [ ] Bill/invoice OCR scanning
- [ ] Customer loyalty CRM
- [ ] Supplier PO automation
- [ ] Multi-language UI (Hindi, Marathi)

### Phase 3 (Month 10-18)
- [ ] Hyperlocal demand signals
- [ ] UPI payment integration
- [ ] ML inventory prediction (scikit-learn + Prophet)
- [ ] Multi-shop chain management
- [ ] Open API for partners
