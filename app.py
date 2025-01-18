from flask import Flask, render_template, jsonify, request, abort, redirect, url_for
from db import products_collection
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime


client = MongoClient(
    "mongodb+srv://smashrafuldev:xQ5BgRtJ4zqQraHI@cluster0.kljdx.mongodb.net/product_store?retryWrites=true&w=majority",
    tls=True,
    tlsAllowInvalidCertificates=False,
)  # Your MongoDB URI
db = client["cart"]


app = Flask(__name__)


@app.route("/")
def home():
    loveProducts = products_collection.find({"category": "Love & Romance"})
    giftProducts = products_collection.find({"category": "gift"})
    return render_template(
        "index.html", loveProducts=loveProducts, giftProducts=giftProducts
    )


@app.route("/love-romance")
def product():
    products = products_collection.find({"category": "Love & Romance"})
    return render_template("loveRomance.html", products=products)


@app.route("/add_to_cart", methods=["POST"])
def add_to_cart():
    user_id = request.form.get("user_id")
    product_id = request.form.get("product_id")

    quantity = int(request.form.get("quantity", 1))

    # Check if the product exists in the products collection
    product = products_collection.find_one({"_id": ObjectId(product_id)})

    if not product:
        return jsonify({"error": "Product not found"}), 404

    # Check if the user already has a cart
    cart = db.carts.find_one({"user_id": user_id})

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
    cart = db.carts.find_one({"user_id": user_id})
    if not cart:
        return jsonify({"message": "Cart is empty"}), 404

    items = []
    for item in cart["items"]:
        product = products_collection.find_one({"_id": ObjectId(item["product_id"])})
        if product:
            items.append(
                {
                    "product_name": product["name"],
                    "product_price": product["price"],
                    "quantity": item["quantity"],
                    "total_price": product["price"] * item["quantity"],
                    "image_url": product["images"][0]["image_url"],
                }
            )
        else:
            print(f"Product ID {item['product_id']} not found.")

    print(f"Items to render: {items}")
    return render_template("cart.html", items=items)


@app.route("/products/<product_id>")
def product_page(product_id):
    try:
        product = products_collection.find_one({"_id": ObjectId(product_id)})
        print(f"New single product: {product}")
        if product:
            return render_template("product.html", product=product)
        else:
            abort(404, description="Product not found")
    except Exception as e:
        abort(400, description="Invalid product ID")


# Checkout route
@app.route("/checkout/<user_id>", methods=["GET", "POST"])
def checkout(user_id):
    cart = db.carts.find_one({"user_id": user_id})
    if not cart:
        return jsonify({"message": "Cart is empty"}), 404

    items = []
    total_price = 0

    # Get cart items
    for item in cart["items"]:
        product = products_collection.find_one({"_id": ObjectId(item["product_id"])})
        if product:
            total_price += product["price"] * item["quantity"]
            items.append(
                {
                    "product_name": product["name"],
                    "product_price": product["price"],
                    "quantity": item["quantity"],
                    "total_price": product["price"] * item["quantity"],
                    "image_url": product["images"][0]["image_url"],
                }
            )

    shipping_charge = 100
    grand_total = total_price + shipping_charge

    if request.method == "POST":
        customer_name = request.form["customer_name"]
        phone = request.form["phone"]
        address = request.form["address"]
        city = request.form["city"]

        # Save the order
        order = {
            "user_id": user_id,
            "customer_name": customer_name,
            "phone": phone,
            "address": address,
            "city": city,
            "items": items,
            "shipping_charge": shipping_charge,
            "total_price": total_price,
            "grand_total": grand_total,
            "order_date": datetime.now(),
        }

        db.orders.insert_one(order)
        db.carts.delete_one({"user_id": user_id})
        return redirect(url_for("my_account", user_id=user_id))

    return render_template(
        "checkout.html",
        items=items,
        total_price=total_price,
        grand_total=grand_total,
        user_id=user_id,
    )


@app.route("/my_account/<user_id>")
def my_account(user_id):
    # Fetch user orders from the database
    orders = list(db.orders.find({"user_id": user_id}))
    print(f"Orders for {user_id}: {orders}")  # Debugging print statement

    # Check if orders exist
    if not orders:
        # Render template with an empty orders list
        return render_template(
            "my_account.html",
            orders=[],
            user_id=user_id,
            message="You have no order data.",
        )

    # Extract order details if orders exist
    order_data = [
        {
            "order_id": str(order["_id"]),
            "order_date": order["order_date"].strftime("%Y-%m-%d %H:%M:%S"),
            "items": order["items"],
            "total_price": order["total_price"],
            "grand_total": order["grand_total"],
            "address": {
                "customer_name": order["customer_name"],
                "phone": order["phone"],
                "address": order["address"],
                "city": order["city"],
            },
        }
        for order in orders
    ]
    print(f"order data of user: ", order_data)
    # Render template with order data
    return render_template("my_account.html", orders=order_data, user_id=user_id)


if __name__ == "__main__":
    app.run(debug=True)
