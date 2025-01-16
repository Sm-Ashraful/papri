from pymongo import MongoClient
from datetime import datetime


# 1. Connect to MongoDB
client = MongoClient(
    "mongodb+srv://smashrafuldev:xQ5BgRtJ4zqQraHI@cluster0.kljdx.mongodb.net/product_store?retryWrites=true&w=majority",
    tls=True,
    tlsAllowInvalidCertificates=False,
)  # Default local MongoDB URI

# 2. Create a Database
db = client["product_store"]  # This creates or selects the 'product_store' database

# 3. Create a Collection
products_collection = db["products"]

# 4. Insert a Sample Product
products = [
    {
        "name": "Romantic Candlelight Set",
        "price": 2500.00,
        "description": "A set of aromatic candles perfect for a romantic evening.",
        "category": "Love & Romance",
        "stock_quantity": 150,
        "is_featured": True,
        "discount": 15.0,
        "offer_start_date": datetime(2025, 2, 1),
        "offer_end_date": datetime(2025, 2, 14),
        "images": [{"image_url": "/assets/love/lov2.jpg"}],
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    },
    {
        "name": "Heart-Shaped Chocolate Box",
        "price": 1800.00,
        "description": "A box of premium chocolates in heart shapes.",
        "category": "Love & Romance",
        "stock_quantity": 200,
        "is_featured": True,
        "discount": 20.0,
        "offer_start_date": datetime(2025, 2, 5),
        "offer_end_date": datetime(2025, 2, 15),
        "images": [{"image_url": "/assets/love/Dive-into-the-Blue-450x450.jpg"}],
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    },
    {
        "name": "Luxury Rose Bouquet",
        "price": 3500.00,
        "description": "A premium bouquet of fresh red roses.",
        "category": "Love & Romance",
        "stock_quantity": 120,
        "is_featured": True,
        "discount": 10.0,
        "offer_start_date": datetime(2025, 2, 10),
        "offer_end_date": datetime(2025, 2, 20),
        "images": [{"image_url": "/assets/love/Circle-of-Love-450x450.jpg"}],
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    },
    {
        "name": "Couple's Spa Gift Set",
        "price": 5000.00,
        "description": "A luxurious spa set for a relaxing time together.",
        "category": "Love & Romance",
        "stock_quantity": 80,
        "is_featured": True,
        "discount": 12.0,
        "offer_start_date": datetime(2025, 1, 20),
        "offer_end_date": datetime(2025, 2, 10),
        "images": [{"image_url": "/assets/love/lov1.jpeg"}],
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    },
    {
        "name": "Personalized Love Photo Frame",
        "price": 1500.00,
        "description": "A customized photo frame for capturing special memories.",
        "category": "Love & Romance",
        "stock_quantity": 300,
        "is_featured": True,
        "discount": 5.0,
        "offer_start_date": datetime(2025, 2, 1),
        "offer_end_date": datetime(2025, 2, 28),
        "images": [{"image_url": "/assets/love/lov2.jpg"}],
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    },
]

# Insert the sample product into the collection
result = products_collection.insert_many(products)
print(f"Inserted Product ID: {result}")

# 5. Fetch and Print All Products
products = products_collection.find()
for product in products:
    print(product)
