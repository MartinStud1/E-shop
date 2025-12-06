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
  "mens-watches"
]

tags = [
    "elegance",
    "energy",
    "city",
    "urban",
    "activity",
    "summer"
]


def get_posts_by_tags(tag):
    url = f"https://dummyjson.com/posts/tag/{tag}"
    response = requests.get(url)

    if response.status_code == 200:
        return response.json().get("posts", [])
    return []





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
    p["group"] = "allwomen"

for p in all_men_products:
    p["group"] = "allmen"

for p in sports_products:
    p["group"] = "allsports"

all_random_products = random_women_products + random_men_products + random_sports_products
random.shuffle(all_random_products)
all_random_products = [p for p in all_random_products if p.get("thumbnail")]

all_products = all_men_products + all_women_products + sports_products

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', products = all_random_products)


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
    # slovník pro unikátní články podle id
    unique_posts = {}

    for tag in tags:
        posts = get_posts_by_tags(tag)
        for post in posts:
        # pokud ještě tento id nemáme, přidáme
            if post['id'] not in unique_posts:
                unique_posts[post['id']] = post

    # převod na seznam unikátních článků
    final_posts = list(unique_posts.values())
    final_posts = random.sample(final_posts, min(len(final_posts), 5))
    return render_template('blog.html', posts = final_posts)

@app.route('/blog/<int:post_id>')
def blog_detail(post_id):
    # Procházíme všechny tagy a hledáme post podle id
    unique_posts = {}
    for tag in tags:
        posts = get_posts_by_tags(tag)
        for post in posts:
            if post['id'] not in unique_posts:
                unique_posts[post['id']] = post

    post = unique_posts.get(post_id)
    if not post:
        return "Post not found", 404

    return render_template('blog-detail.html', post=post)

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