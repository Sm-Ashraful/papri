from flask import Flask, render_template, jsonify, request
from db import products_collection
from pymongo import MongoClient
from bson import ObjectId

client = MongoClient(
    "mongodb+srv://smashrafuldev:xQ5BgRtJ4zqQraHI@cluster0.kljdx.mongodb.net/product_store?retryWrites=true&w=majority",
    tls=True,
    tlsAllowInvalidCertificates=False,
)  # Your MongoDB URI
db = client["cart"]

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/love-romance")
def product():
    products = products_collection.find({"category": "Love & Romance"})
    return render_template("loveRomance.html", products=products)


@app.route("/add_to_cart", methods=["POST"])
def add_to_cart():
    user_id = request.form.get("user_id")
    product_id = request.form.get("product_id")
    print(f"Product ID: {product_id}")
    quantity = int(request.form.get("quantity", 1))

    # Check if the product exists in the products collection
    product = products_collection.find_one({"_id": ObjectId(product_id)})

    if not product:
        return jsonify({"error": "Product not found"}), 404

    # Check if the user already has a cart
    cart = db.carts.find_one({"user_id": user_id})

    print(f"Product page: {cart}")
    if cart:
        # Check if the product is already in the cart
        existing_item = next(
            (item for item in cart["items"] if item["product_id"] == product_id),
            None,
        )

        if existing_item:
            # Update the quantity of the existing item
            db.carts.update_one(
                {"user_id": user_id, "items.product_id": product_id},
                {"$inc": {"items.$.quantity": quantity}},
            )
        else:
            # Add new item to the cart
            db.carts.update_one(
                {"user_id": user_id},
                {
                    "$push": {
                        "items": {
                            "product_id": product_id,
                            "quantity": quantity,
                        }
                    }
                },
            )
    else:
        # Create a new cart if the user doesn't have one
        db.carts.insert_one(
            {
                "user_id": user_id,
                "items": [{"product_id": product_id, "quantity": quantity}],
            }
        )
    return jsonify({"message": "Item added to cart"}), 200


@app.route("/view_cart/<user_id>", methods=["GET"])
def view_cart(user_id):
    # Find the user's cart
    cart = db.carts.find_one({"user_id": user_id})
    print(cart)
    if not cart:
        return jsonify({"message": "Cart is empty"}), 404

    # Fetch product details for the items in the cart
    items = []
    for item in cart["items"]:
        product = products_collection.find_one({"_id": ObjectId(item["product_id"])})
        if product:
            item_details = {
                "product_name": product["name"],
                "product_price": product["price"],
                "quantity": item["quantity"],
                "total_price": product["price"] * item["quantity"],
                "image_url": product["images"][0]["image_url"],
            }
            items.append(item_details)

    return render_template("cart.html", items=items)


if __name__ == "__main__":
    app.run(debug=True)
