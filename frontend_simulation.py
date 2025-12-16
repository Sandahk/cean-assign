import requests
import random
import time

API = "http://localhost:8000"

def print_banner(msg):
    print("\n" + "="*len(msg))
    print(msg)
    print("="*len(msg))

def list_products():
    print_banner("1. Fetch Products")
    resp = requests.get(f"{API}/products")
    products = resp.json()
    for p in products:
        print(f"ID {p['id']}: {p['name']} (Price: {p['price']}) | Kit: {p['is_kit']} | Colors: {p.get('colors', [])}")
    return products

def build_quote(products):
    print_banner("2. Build a Quote (mimic UI logic)")
    items = []
    # Add 1 basic product
    p1 = next(p for p in products if not p['is_kit'] and not p['has_colors'])
    items.append({"product_id": p1['id'], "quantity": 1})

    # Add 1 color product (pick random color)
    color_prod = next(p for p in products if p['has_colors'])
    color_choice = random.choice(color_prod['colors'])
    items.append({"product_id": color_prod['id'], "quantity": 2, "color": color_choice})

    # Add a kit, reordering its components (reverse)
    kit = next(p for p in products if p['is_kit'])
    kit_order = list(reversed(kit['kit_components']))
    items.append({"product_id": kit['id'], "quantity": 1, "kit_order": kit_order})

    customer = f"TestUser{random.randint(1000,9999)}"
    quote = {"customer": customer, "items": items}
    print(f"Quote to send:\n{quote}")
    return quote

def create_quote(quote):
    print_banner("3. POST /quotes")
    resp = requests.post(f"{API}/quotes", json=quote)
    print("Response:", resp.json())
    return resp.json().get("id")

def fetch_quote(quote_id):
    print_banner("4. GET /quotes/{id}")
    resp = requests.get(f"{API}/quotes/{quote_id}")
    print("Quote details:")
    print(resp.json())

if __name__ == "__main__":
    products = list_products()
    time.sleep(1)
    quote = build_quote(products)
    time.sleep(1)
    quote_id = create_quote(quote)
    time.sleep(1)
    if quote_id:
        fetch_quote(quote_id)
