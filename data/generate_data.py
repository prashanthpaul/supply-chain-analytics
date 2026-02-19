"""
Supply Chain Analytics — Synthetic Data Generator
Generates realistic supply chain data: orders, products, suppliers, customers, shipments
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

random.seed(42)
np.random.seed(42)

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "raw")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ─────────────────────────────────────────
# SUPPLIERS
# ─────────────────────────────────────────
SUPPLIERS = [
    {"supplier_id": f"S{i:03d}", "supplier_name": name, "country": country,
     "lead_time_days": lt, "reliability_score": rs, "category": cat}
    for i, (name, country, lt, rs, cat) in enumerate([
        ("GlobalTech Parts",       "China",       14, 0.88, "Electronics"),
        ("QuickShip Logistics",    "USA",          3, 0.96, "Logistics"),
        ("EuroComponents GmbH",    "Germany",      7, 0.93, "Electronics"),
        ("AsiaPac Supplies",       "Vietnam",     10, 0.81, "Raw Materials"),
        ("FastTrack Fulfillment",  "USA",          2, 0.97, "Logistics"),
        ("MexiParts SA",           "Mexico",       5, 0.90, "Automotive"),
        ("IndoTextiles Ltd",       "India",       12, 0.79, "Textiles"),
        ("Nordic Materials AB",    "Sweden",       8, 0.94, "Raw Materials"),
        ("PacRim Electronics",     "South Korea",  9, 0.91, "Electronics"),
        ("Southern Plastics Co",   "Brazil",       6, 0.85, "Plastics"),
        ("GreatWall Manufacturing","China",        15, 0.76, "Heavy Equipment"),
        ("MidWest Steel Inc",      "USA",          4, 0.92, "Raw Materials"),
    ], start=1)
]

# ─────────────────────────────────────────
# PRODUCTS
# ─────────────────────────────────────────
PRODUCT_DATA = [
    ("Laptop Pro 15",       "Electronics",  "Computers",    450, 899),
    ("Wireless Headset",    "Electronics",  "Audio",         35, 89),
    ("Office Chair Ergx",   "Furniture",    "Seating",       85, 249),
    ("Steel Beam 10ft",     "Raw Materials","Metal",         40, 95),
    ("Cotton Fabric 10m",   "Textiles",     "Fabric",        18, 42),
    ("Auto Brake Kit",      "Automotive",   "Parts",         55, 130),
    ("PVC Pipe 2in",        "Plastics",     "Piping",         8, 22),
    ("Solar Panel 300W",    "Electronics",  "Energy",        95, 249),
    ("Standing Desk",       "Furniture",    "Desks",        120, 399),
    ("Hydraulic Pump",      "Heavy Equip",  "Machinery",    280, 650),
    ("LED Flood Light",     "Electronics",  "Lighting",      25, 65),
    ("Shipping Pallet",     "Logistics",    "Packaging",      8, 18),
    ("Thermal Sensor",      "Electronics",  "Sensors",       30, 85),
    ("Aluminum Sheet 4x8",  "Raw Materials","Metal",         45, 110),
    ("Safety Helmet",       "Safety",       "PPE",            9, 28),
    ("Network Switch 24p",  "Electronics",  "Networking",    95, 249),
    ("Forklift Battery",    "Heavy Equip",  "Power",        180, 425),
    ("Polyester Resin 5kg", "Plastics",     "Resin",         22, 55),
    ("Conveyor Belt 5m",    "Heavy Equip",  "Machinery",    210, 520),
    ("Fire Extinguisher",   "Safety",       "Safety",        18, 49),
]

products = []
for i, (name, cat, subcat, cost, price) in enumerate(PRODUCT_DATA, start=1):
    products.append({
        "product_id":   f"P{i:03d}",
        "product_name":  name,
        "category":      cat,
        "sub_category":  subcat,
        "unit_cost":     cost,
        "unit_price":    price,
        "supplier_id":   f"S{random.randint(1,12):03d}",
    })

# ─────────────────────────────────────────
# CUSTOMERS
# ─────────────────────────────────────────
CUSTOMER_NAMES = [
    "Apex Industries", "BlueStar Corp", "Cardinal Systems", "Delta Dynamics",
    "Echo Enterprises", "Falcon Tech", "Granite Solutions", "Harbor Holdings",
    "Ironclad Ltd", "Juniper Networks", "Keystone Partners", "Liberty Goods",
    "Meridian Corp", "Nexus Industries", "Omega Supply Co", "Pioneer Parts",
    "Quantum Tech", "Redwood Manufacturing", "Sterling Logistics", "Titan Corp",
    "Unified Goods", "Vertex Holdings", "Westbrook Inc", "Xenon Systems",
    "Yellowstone Co", "Zenith Enterprises", "Atlas Global", "Beacon Industries",
    "Cobalt Dynamics", "Drake Manufacturing",
]
SEGMENTS  = ["Enterprise", "Mid-Market", "SMB"]
REGIONS   = ["North America", "Europe", "Asia Pacific", "Latin America", "Middle East"]
CITIES    = {
    "North America": ["New York", "Los Angeles", "Chicago", "Houston", "Toronto"],
    "Europe":        ["London", "Paris", "Berlin", "Amsterdam", "Madrid"],
    "Asia Pacific":  ["Singapore", "Tokyo", "Sydney", "Mumbai", "Shanghai"],
    "Latin America": ["São Paulo", "Mexico City", "Bogotá", "Lima", "Buenos Aires"],
    "Middle East":   ["Dubai", "Riyadh", "Istanbul", "Cairo", "Tel Aviv"],
}

customers = []
for i, name in enumerate(CUSTOMER_NAMES, start=1):
    region = random.choice(REGIONS)
    customers.append({
        "customer_id":   f"C{i:03d}",
        "customer_name":  name,
        "segment":        random.choice(SEGMENTS),
        "region":         region,
        "city":           random.choice(CITIES[region]),
    })

# ─────────────────────────────────────────
# ORDERS + SHIPMENTS
# ─────────────────────────────────────────
CARRIERS    = ["DHL", "FedEx", "UPS", "USPS", "Maersk", "Kuehne+Nagel"]
STATUSES    = ["Delivered", "Delivered", "Delivered", "Shipped", "Processing", "Cancelled"]
START_DATE  = datetime(2022, 1, 1)
END_DATE    = datetime(2024, 12, 31)

orders, shipments = [], []
for i in range(1, 10001):
    order_date  = START_DATE + timedelta(days=random.randint(0, (END_DATE - START_DATE).days))
    product     = random.choice(products)
    customer    = random.choice(customers)
    supplier    = next(s for s in SUPPLIERS if s["supplier_id"] == product["supplier_id"])
    lead_days   = supplier["lead_time_days"] + random.randint(-2, 5)
    ship_date   = order_date + timedelta(days=random.randint(1, 3))
    est_del     = ship_date + timedelta(days=lead_days)
    reliability = supplier["reliability_score"]
    delay_days  = 0 if random.random() < reliability else random.randint(1, 10)
    act_del     = est_del + timedelta(days=delay_days)
    on_time     = delay_days == 0
    qty         = random.randint(1, 50)
    discount    = random.choice([0, 0, 0, 0.05, 0.10, 0.15])
    status      = random.choice(STATUSES)

    orders.append({
        "order_id":       f"ORD{i:05d}",
        "order_date":     order_date.date(),
        "ship_date":      ship_date.date(),
        "status":         status,
        "customer_id":    customer["customer_id"],
        "customer_name":  customer["customer_name"],
        "segment":        customer["segment"],
        "region":         customer["region"],
        "city":           customer["city"],
        "product_id":     product["product_id"],
        "product_name":   product["product_name"],
        "category":       product["category"],
        "sub_category":   product["sub_category"],
        "supplier_id":    supplier["supplier_id"],
        "supplier_name":  supplier["supplier_name"],
        "supplier_country": supplier["country"],
        "quantity":       qty,
        "unit_cost":      product["unit_cost"],
        "unit_price":     product["unit_price"],
        "discount":       discount,
        "revenue":        round(qty * product["unit_price"] * (1 - discount), 2),
        "cogs":           round(qty * product["unit_cost"], 2),
    })

    shipments.append({
        "shipment_id":         f"SHP{i:05d}",
        "order_id":            f"ORD{i:05d}",
        "carrier":             random.choice(CARRIERS),
        "ship_date":           ship_date.date(),
        "estimated_delivery":  est_del.date(),
        "actual_delivery":     act_del.date() if status not in ["Processing", "Cancelled"] else None,
        "on_time":             on_time if status == "Delivered" else None,
        "delay_days":          delay_days if status == "Delivered" else None,
        "shipment_cost":       round(random.uniform(10, 150), 2),
    })

# ─────────────────────────────────────────
# SAVE TO CSV
# ─────────────────────────────────────────
dfs = {
    "suppliers":  pd.DataFrame(SUPPLIERS),
    "products":   pd.DataFrame(products),
    "customers":  pd.DataFrame(customers),
    "orders":     pd.DataFrame(orders),
    "shipments":  pd.DataFrame(shipments),
}

for name, df in dfs.items():
    path = os.path.join(OUTPUT_DIR, f"{name}.csv")
    df.to_csv(path, index=False)
    print(f"✅  {name}.csv  ({len(df):,} rows)  →  {path}")

print("\n✅  All data generated successfully.")
