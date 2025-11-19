from flask import Flask, render_template, jsonify
import requests
import random

women_categories = [
  "womens-bags",
  "womens-dresses",
  "womens-jewellery",
  "womens-shoes",
  "womens-watches"
]

men_categories = [
  "mens-shirts",
  "mens-shoes",
  "mens-watches",
]



def get_products_from_category(category):
    url = f'https://dummyjson.com/products/category/{category}'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        return data.get('products', [])
    else:
        return []

def get_all_products_from_categories(categories):
    all_products = []
    for category in categories:
        products = get_products_from_category(category)
        all_products = all_products + products
    return all_products


all_women_products = get_all_products_from_categories(women_categories)
random_women_products = random.sample(all_women_products, min(4, len(all_women_products)))

all_men_products = get_all_products_from_categories(men_categories)
random_men_products = random.sample(all_men_products, min(4, len(all_men_products)))

sports_products = get_products_from_category("sports-accessories")
random_sports_products = random.sample(sports_products, min(4, len(sports_products)))

for p in random_women_products:
    p["rndgroup"] = "women"

for p in random_men_products:
    p["rndgroup"] = "men"

for p in random_sports_products:
    p["rndgroup"] = "sports"


for p in all_women_products:
    p["group"] = "women"

for p in all_men_products:
    p["group"] = "men"

for p in sports_products:
    p["group"] = "sports"

all_random_products = random_women_products + random_men_products + random_sports_products
random.shuffle(all_random_products)

for product in random_women_products:
    print(product["id"])
print("Počet produktů ve všech women kategoriích:", len(all_women_products))
print("Počet produktů ve všech women kategoriích:", len(all_men_products))


all_products = all_men_products + all_women_products + sports_products

all_products = all_men_products + all_women_products + sports_products

for product in all_products:
    product_id = product.get('id', 'neznámé ID')
    title = product.get('title', 'Bez názvu')
    images = product.get('images', [])
    print(f"Produkt ID {product_id} ('{title}') má {len(images)} obrázků.")

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', products = all_random_products)



@app.route('/api/product/<int:product_id>')
def get_product(product_id):
    # Volání DummyJSON API
    api_url = f"https://dummyjson.com/products/{product_id}"
    response = requests.get(api_url)

    if response.status_code != 200:
        return jsonify({"error": "Produkt nenalezen"}), 404

    data = response.json()

    # Vytvoření výsledného JSONu
    product = {
        "id": data.get("id"),
        "title": data.get("title"),
        "price": data.get("price"),
        "description": data.get("description"),
        "images": data.get("images", []),             # pole URL obrázků
        "num_images": len(data.get("images", []))    # počet obrázků
    }

    return jsonify(product)



@app.route("/home-02")
def home_02():
    return render_template("home-02.html")

@app.route("/home-03")
def home_03():
    return render_template("home-03.html")

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/blog')
def blog():
    return render_template('blog.html')

@app.route('/blog-detail')
def blog_detail():
    return render_template('blog-detail.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/product')
def product():
    random.shuffle(all_products)
    return render_template('product.html', products = all_products)

@app.route('/product-detail')
def product_detail():
    return render_template('product-detail.html')

@app.route('/shopping-cart')
def shopping_cart():
    return render_template('shopping-cart.html')

if __name__ == '__main__':
    app.run(debug=True)