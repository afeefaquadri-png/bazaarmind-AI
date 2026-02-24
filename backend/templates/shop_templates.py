"""
Centralized shop type configuration.
Add new shop types here — no code changes needed elsewhere.
"""

SHOP_TEMPLATES = {
    # ── Retail ──────────────────────────────────────────────────────────────
    "kirana": {
        "label": "Kirana / Grocery Store",
        "icon": "🛒",
        "category": "retail",
        "attributes": [
            {"key": "expiry_date",  "label": "Expiry Date",   "type": "date",   "required": True},
            {"key": "weight",       "label": "Weight (g/kg)", "type": "text",   "required": False},
            {"key": "brand",        "label": "Brand",         "type": "text",   "required": False},
            {"key": "mrp",          "label": "MRP (Rs.)",     "type": "number", "required": False},
        ],
        "low_stock_threshold": 10,
        "units": ["piece", "kg", "litre", "packet", "dozen"],
    },
    "supermarket": {
        "label": "Supermarket",
        "icon": "🏪",
        "category": "retail",
        "attributes": [
            {"key": "expiry_date",  "label": "Expiry Date",   "type": "date",   "required": True},
            {"key": "brand",        "label": "Brand",         "type": "text",   "required": True},
            {"key": "barcode",      "label": "Barcode",       "type": "text",   "required": False},
            {"key": "mrp",          "label": "MRP (Rs.)",     "type": "number", "required": True},
            {"key": "category",     "label": "Category",      "type": "select", "required": True,
             "options": ["Food", "Beverages", "Personal Care", "Household", "Dairy", "Snacks"]},
        ],
        "low_stock_threshold": 15,
        "units": ["piece", "kg", "litre", "packet"],
    },
    "general_store": {
        "label": "General Store",
        "icon": "🏬",
        "category": "retail",
        "attributes": [
            {"key": "brand",    "label": "Brand",         "type": "text",   "required": False},
            {"key": "category", "label": "Category",      "type": "text",   "required": False},
        ],
        "low_stock_threshold": 5,
        "units": ["piece", "set", "packet"],
    },

    # ── Fashion ──────────────────────────────────────────────────────────────
    "clothing": {
        "label": "Clothing Store",
        "icon": "👕",
        "category": "fashion",
        "attributes": [
            {"key": "size",    "label": "Size",    "type": "select", "required": True,
             "options": ["XS", "S", "M", "L", "XL", "XXL", "XXXL", "Free Size"]},
            {"key": "color",   "label": "Color",   "type": "text",   "required": True},
            {"key": "brand",   "label": "Brand",   "type": "text",   "required": False},
            {"key": "gender",  "label": "Gender",  "type": "select", "required": False,
             "options": ["Men", "Women", "Kids", "Unisex"]},
            {"key": "fabric",  "label": "Fabric",  "type": "text",   "required": False},
        ],
        "low_stock_threshold": 3,
        "units": ["piece", "set", "dozen"],
    },
    "footwear": {
        "label": "Footwear Shop",
        "icon": "👟",
        "category": "fashion",
        "attributes": [
            {"key": "size",     "label": "Size (UK/IN)", "type": "select", "required": True,
             "options": ["5", "6", "7", "8", "9", "10", "11", "12"]},
            {"key": "color",    "label": "Color",        "type": "text",   "required": True},
            {"key": "material", "label": "Material",     "type": "text",   "required": False},
            {"key": "brand",    "label": "Brand",        "type": "text",   "required": False},
            {"key": "gender",   "label": "Gender",       "type": "select", "required": False,
             "options": ["Men", "Women", "Kids", "Unisex"]},
        ],
        "low_stock_threshold": 2,
        "units": ["pair", "piece"],
    },
    "boutique": {
        "label": "Boutique",
        "icon": "👗",
        "category": "fashion",
        "attributes": [
            {"key": "size",          "label": "Size",            "type": "text",   "required": True},
            {"key": "color",         "label": "Color",           "type": "text",   "required": True},
            {"key": "fabric",        "label": "Fabric",          "type": "text",   "required": False},
            {"key": "occasion",      "label": "Occasion",        "type": "select", "required": False,
             "options": ["Casual", "Formal", "Wedding", "Festival", "Party"]},
            {"key": "design_code",   "label": "Design Code",     "type": "text",   "required": False},
        ],
        "low_stock_threshold": 2,
        "units": ["piece", "set"],
    },

    # ── Automotive ────────────────────────────────────────────────────────────
    "auto_parts": {
        "label": "Auto Parts Shop",
        "icon": "🔧",
        "category": "automotive",
        "attributes": [
            {"key": "vehicle_model", "label": "Vehicle Model", "type": "text",   "required": True},
            {"key": "part_number",   "label": "Part Number",   "type": "text",   "required": True},
            {"key": "brand",         "label": "Brand",         "type": "text",   "required": False},
            {"key": "compatibility", "label": "Compatible With","type": "text",   "required": False},
            {"key": "oem",           "label": "OEM/Aftermarket","type": "select", "required": False,
             "options": ["OEM", "Aftermarket", "Refurbished"]},
        ],
        "low_stock_threshold": 5,
        "units": ["piece", "set", "litre"],
    },
    "bike_repair": {
        "label": "Bike Repair Shop",
        "icon": "🏍️",
        "category": "automotive",
        "attributes": [
            {"key": "bike_model",  "label": "Bike Model",  "type": "text",   "required": True},
            {"key": "part_number", "label": "Part Number", "type": "text",   "required": False},
            {"key": "brand",       "label": "Brand",       "type": "text",   "required": False},
        ],
        "low_stock_threshold": 3,
        "units": ["piece", "set", "litre"],
    },
    "car_service": {
        "label": "Car Service Center",
        "icon": "🚗",
        "category": "automotive",
        "attributes": [
            {"key": "car_model",   "label": "Car Model",    "type": "text",   "required": True},
            {"key": "part_number", "label": "Part Number",  "type": "text",   "required": False},
            {"key": "brand",       "label": "Brand",        "type": "text",   "required": False},
            {"key": "service_type","label": "Service Type", "type": "select", "required": False,
             "options": ["Engine", "Transmission", "Brakes", "Electrical", "Body", "Tyres", "AC"]},
        ],
        "low_stock_threshold": 5,
        "units": ["piece", "set", "litre", "kg"],
    },

    # ── Food & Beverage ───────────────────────────────────────────────────────
    "restaurant": {
        "label": "Restaurant",
        "icon": "🍽️",
        "category": "food",
        "attributes": [
            {"key": "veg_nonveg",    "label": "Veg/Non-Veg", "type": "select", "required": True,
             "options": ["Veg", "Non-Veg", "Egg", "Vegan"]},
            {"key": "portion_size",  "label": "Portion Size", "type": "select", "required": False,
             "options": ["Small", "Medium", "Large", "Full", "Half"]},
            {"key": "spice_level",   "label": "Spice Level",  "type": "select", "required": False,
             "options": ["Mild", "Medium", "Spicy", "Extra Spicy"]},
            {"key": "cuisine",       "label": "Cuisine Type", "type": "text",   "required": False},
        ],
        "low_stock_threshold": 5,
        "units": ["plate", "piece", "litre", "kg"],
    },
    "street_food": {
        "label": "Street Food / Dhaba",
        "icon": "🌮",
        "category": "food",
        "attributes": [
            {"key": "veg_nonveg",  "label": "Veg/Non-Veg",  "type": "select", "required": True,
             "options": ["Veg", "Non-Veg", "Egg"]},
            {"key": "portion_size","label": "Portion Size",  "type": "select", "required": False,
             "options": ["Small", "Regular", "Large"]},
        ],
        "low_stock_threshold": 5,
        "units": ["plate", "piece"],
    },
    "bakery": {
        "label": "Bakery",
        "icon": "🥐",
        "category": "food",
        "attributes": [
            {"key": "expiry_date", "label": "Best Before",  "type": "date",   "required": True},
            {"key": "flavor",      "label": "Flavor",       "type": "text",   "required": False},
            {"key": "weight",      "label": "Weight (g)",   "type": "number", "required": False},
            {"key": "eggless",     "label": "Eggless",      "type": "select", "required": False,
             "options": ["Yes", "No"]},
        ],
        "low_stock_threshold": 5,
        "units": ["piece", "kg", "dozen", "packet"],
    },
    "cafe": {
        "label": "Cafe / Coffee Shop",
        "icon": "☕",
        "category": "food",
        "attributes": [
            {"key": "size",         "label": "Cup Size",    "type": "select", "required": True,
             "options": ["Small", "Medium", "Large", "Extra Large"]},
            {"key": "hot_cold",     "label": "Hot/Cold",    "type": "select", "required": False,
             "options": ["Hot", "Cold", "Both"]},
            {"key": "dairy_free",   "label": "Dairy-Free",  "type": "select", "required": False,
             "options": ["Yes", "No", "Optional"]},
        ],
        "low_stock_threshold": 5,
        "units": ["cup", "piece", "litre"],
    },

    # ── Health & Pharma ───────────────────────────────────────────────────────
    "pharmacy": {
        "label": "Pharmacy",
        "icon": "💊",
        "category": "health",
        "attributes": [
            {"key": "expiry_date",   "label": "Expiry Date",   "type": "date",   "required": True},
            {"key": "dosage",        "label": "Dosage",        "type": "text",   "required": True},
            {"key": "manufacturer",  "label": "Manufacturer",  "type": "text",   "required": True},
            {"key": "prescription",  "label": "Rx Required",   "type": "select", "required": True,
             "options": ["Yes", "No", "OTC"]},
            {"key": "salt_name",     "label": "Salt/Generic",  "type": "text",   "required": False},
        ],
        "low_stock_threshold": 10,
        "units": ["strip", "bottle", "tube", "piece", "packet"],
    },
    "medical_store": {
        "label": "Medical Store",
        "icon": "🏥",
        "category": "health",
        "attributes": [
            {"key": "expiry_date",  "label": "Expiry Date",   "type": "date",   "required": True},
            {"key": "manufacturer", "label": "Manufacturer",  "type": "text",   "required": True},
            {"key": "category",     "label": "Category",      "type": "select", "required": False,
             "options": ["Medicine", "Equipment", "Surgical", "Wellness", "Baby Care"]},
        ],
        "low_stock_threshold": 10,
        "units": ["piece", "strip", "bottle", "packet"],
    },

    # ── Home & Hardware ───────────────────────────────────────────────────────
    "hardware_store": {
        "label": "Hardware Store",
        "icon": "🔨",
        "category": "home",
        "attributes": [
            {"key": "material",    "label": "Material",     "type": "text",   "required": False},
            {"key": "usage_type",  "label": "Usage Type",   "type": "text",   "required": False},
            {"key": "brand",       "label": "Brand",        "type": "text",   "required": False},
            {"key": "size_spec",   "label": "Size / Spec",  "type": "text",   "required": False},
        ],
        "low_stock_threshold": 5,
        "units": ["piece", "set", "kg", "metre", "litre", "bag"],
    },
    "electrical_shop": {
        "label": "Electrical Shop",
        "icon": "⚡",
        "category": "home",
        "attributes": [
            {"key": "wattage",     "label": "Wattage/Rating","type": "text",   "required": False},
            {"key": "brand",       "label": "Brand",         "type": "text",   "required": False},
            {"key": "voltage",     "label": "Voltage",       "type": "select", "required": False,
             "options": ["5V", "12V", "24V", "110V", "220V", "240V"]},
            {"key": "warranty",    "label": "Warranty",      "type": "text",   "required": False},
        ],
        "low_stock_threshold": 5,
        "units": ["piece", "metre", "set"],
    },
    "furniture_store": {
        "label": "Furniture Store",
        "icon": "🪑",
        "category": "home",
        "attributes": [
            {"key": "material",    "label": "Material",      "type": "text",   "required": True},
            {"key": "dimensions",  "label": "Dimensions",    "type": "text",   "required": False},
            {"key": "color",       "label": "Color/Finish",  "type": "text",   "required": False},
            {"key": "assembly",    "label": "Assembly Req'd","type": "select", "required": False,
             "options": ["Yes", "No"]},
        ],
        "low_stock_threshold": 2,
        "units": ["piece", "set"],
    },

    # ── Electronics ───────────────────────────────────────────────────────────
    "mobile_shop": {
        "label": "Mobile / Phone Shop",
        "icon": "📱",
        "category": "electronics",
        "attributes": [
            {"key": "brand",    "label": "Brand",      "type": "text",   "required": True},
            {"key": "model",    "label": "Model",      "type": "text",   "required": True},
            {"key": "ram",      "label": "RAM",        "type": "select", "required": False,
             "options": ["2GB", "3GB", "4GB", "6GB", "8GB", "12GB", "16GB"]},
            {"key": "storage",  "label": "Storage",   "type": "select", "required": False,
             "options": ["32GB", "64GB", "128GB", "256GB", "512GB", "1TB"]},
            {"key": "color",    "label": "Color",      "type": "text",   "required": False},
            {"key": "warranty", "label": "Warranty",   "type": "text",   "required": False},
        ],
        "low_stock_threshold": 3,
        "units": ["piece"],
    },
    "electronics_store": {
        "label": "Electronics Store",
        "icon": "💻",
        "category": "electronics",
        "attributes": [
            {"key": "brand",    "label": "Brand",       "type": "text",   "required": True},
            {"key": "model",    "label": "Model No.",   "type": "text",   "required": True},
            {"key": "warranty", "label": "Warranty",    "type": "text",   "required": True},
            {"key": "voltage",  "label": "Voltage",     "type": "text",   "required": False},
            {"key": "category", "label": "Category",   "type": "select", "required": False,
             "options": ["TV", "Laptop", "Tablet", "Camera", "Audio", "AC", "Refrigerator", "Washing Machine", "Other"]},
        ],
        "low_stock_threshold": 3,
        "units": ["piece", "set"],
    },

    # ── Others ────────────────────────────────────────────────────────────────
    "stationery": {
        "label": "Stationery Shop",
        "icon": "📚",
        "category": "others",
        "attributes": [
            {"key": "brand",     "label": "Brand",        "type": "text",   "required": False},
            {"key": "color",     "label": "Color",        "type": "text",   "required": False},
            {"key": "size",      "label": "Size",         "type": "text",   "required": False},
        ],
        "low_stock_threshold": 10,
        "units": ["piece", "packet", "dozen", "set", "book"],
    },
    "gift_shop": {
        "label": "Gift Shop",
        "icon": "🎁",
        "category": "others",
        "attributes": [
            {"key": "occasion",  "label": "Occasion",     "type": "text",   "required": False},
            {"key": "color",     "label": "Color",        "type": "text",   "required": False},
            {"key": "material",  "label": "Material",     "type": "text",   "required": False},
        ],
        "low_stock_threshold": 3,
        "units": ["piece", "set", "pack"],
    },
    "cosmetics": {
        "label": "Cosmetics / Beauty Store",
        "icon": "💄",
        "category": "others",
        "attributes": [
            {"key": "shade",      "label": "Shade/Color",  "type": "text",   "required": False},
            {"key": "skin_type",  "label": "Skin Type",    "type": "select", "required": False,
             "options": ["All Types", "Dry", "Oily", "Combination", "Sensitive", "Normal"]},
            {"key": "brand",      "label": "Brand",        "type": "text",   "required": True},
            {"key": "expiry_date","label": "Expiry Date",  "type": "date",   "required": True},
            {"key": "volume",     "label": "Volume/Weight","type": "text",   "required": False},
        ],
        "low_stock_threshold": 5,
        "units": ["piece", "bottle", "tube", "set"],
    },
}

def get_template(shop_type: str) -> dict:
    return SHOP_TEMPLATES.get(shop_type, {
        "label": shop_type.replace("_", " ").title(),
        "icon": "🏪",
        "category": "general",
        "attributes": [],
        "low_stock_threshold": 5,
        "units": ["piece"],
    })

def get_all_shop_types() -> list:
    result = []
    for key, val in SHOP_TEMPLATES.items():
        result.append({
            "type": key,
            "label": val["label"],
            "icon": val["icon"],
            "category": val["category"],
        })
    return result

def get_categories() -> dict:
    cats = {}
    for key, val in SHOP_TEMPLATES.items():
        cat = val["category"]
        if cat not in cats:
            cats[cat] = []
        cats[cat].append({"type": key, "label": val["label"], "icon": val["icon"]})
    return cats
