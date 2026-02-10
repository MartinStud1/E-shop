from flask import Flask, render_template, jsonify, session, redirect, url_for, request
import requests
import random


registered_users = []


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

def get_current_user_cart():
    # Pokud je uživatel přihlášen, najdeme jeho košík v seznamu
    if 'email' in session:
        for user in registered_users:
            if user['email'] == session['email']:
                # IMPORTANT: Set session['cart'] so templates can access it
                session['cart'] = user['user_cart']
                session.modified = True
                return user['user_cart']
    
    # Pokud není přihlášen, vrátíme (nebo vytvoříme) košík v session
    if 'cart' not in session:
        session['cart'] = []
    return session['cart']


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
app.secret_key = "tajnyklic"

@app.context_processor
def inject_cart_count():
    # Tady se rozhoduje, co uvidí JS i HTML
    cart = []
    if 'email' in session:
        # Pokud je v session email, MUSÍME brát košík z registered_users
        for user in registered_users:
            if user['email'] == session['email']:
                cart = user['user_cart']
                break
    else:
        # Pokud není email, bereme anonymní session
        cart = session.get('cart', [])

    total_qty = sum(item.get('quantity', 0) for item in cart)
    # Tohle posílá data do TVÝCH bublin a mini košíku
    return {
        "cart": cart,
        "cart_count": total_qty,
        "cart_total_price": sum(item.get('quantity', 0) * item.get('price', 0) for item in cart)
    }

@app.route('/')
def index():
    # Ensure session cart exists (templates access session.get('cart') directly)
    get_current_user_cart()
    return render_template('index.html', products = all_random_products)

# --- REGISTRACE ---
@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Kontrola, zda hesla sedí
        if password != confirm_password:
            return render_template('registration.html', error="Hesla se neshodují.")

        # Kontrola, zda uživatel s tímto e-mailem už neexistuje
        for user in registered_users:
            if user['email'] == email:
                return render_template('registration.html', error="Uživatel s tímto e-mailem již existuje.")

        # Přidání nového uživatele do seznamu (včetně jeho budoucího košíku)
        registered_users.append({
            "username": username,
            "email": email,
            "password": password,
            "user_cart": []  # Každý uživatel má své pole pro košík
        })

        print(f"Nový uživatel: {username}, Celkem registrovaných: {len(registered_users)}")
        return redirect(url_for('login'))

    return render_template('registration.html')

@app.route('/logout')
def logout():
    # Smažeme jen konkrétní věci, ne celou session
    session.pop('username', None)
    session.pop('email', None)
    session.pop('cart_count', None)
    
    # Důležité: inicializujeme prázdný košík pro anonyma
    session['cart'] = []
    
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        get_current_user_cart()
        

        for user in registered_users:
            if user['email'] == email and user['password'] == password:
                # 1. Klasické přihlášení
                session['username'] = user['username']
                session['email'] = user['email']
                
                # 2. KLÍČOVÝ KROK: Vyčistíme anonymní košík ze session
                # Tím zajistíme, že se minikošík začne řídit daty z registered_users
                session.pop('cart', None)
                
                # 3. Aktualizujeme počitadlo podle skutečného obsahu uživatelova košíku
                user_cart = user.get('user_cart', [])
                session['cart_count'] = sum(item.get('quantity', 0) for item in user_cart)
                
                # Pro jistotu vynutíme uložení session
                session.modified = True
                
                print(f"DEBUG: Login successful for {user['username']}, Cart count: {session['cart_count']}")
                return redirect(url_for('index'))
        
        return render_template('login.html', error="Invalid email or password.")

    return render_template('login.html')

@app.route('/about')
def about():
    get_current_user_cart()
    return render_template('about.html')

@app.route('/blog')
def blog():
    get_current_user_cart()
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
    get_current_user_cart()
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
    get_current_user_cart()
    return render_template('contact.html')

@app.route('/product')
def product():
    # Ensure the current user's cart is synced into the session so templates
    # that read `session.get('cart')` show the latest data (important after AJAX).
    get_current_user_cart()
    random.shuffle(all_products)
    return render_template('product.html', products = all_products)

@app.route('/product-detail')
def product_detail():
    # Sync cart for product detail page as well
    get_current_user_cart()
    return render_template('product-detail.html')

@app.route('/shopping-cart')
def shopping_cart():
    cart = get_current_user_cart()
    # Spočítáme celkovou cenu pro jistotu i tady
    total_price = sum(item.get('quantity', 0) * item.get('price', 0) for item in cart)
    return render_template('shopping-cart.html', cart=cart, total_price=total_price)

@app.route('/add-to-cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    product = next((p for p in all_products if p['id'] == product_id), None)
    if not product:
        return jsonify({"success": False, "message": "Produkt nenalezen"}), 404

    cart = get_current_user_cart()

    # Logika přidání nebo navýšení množství
    for item in cart:
        if item['id'] == product_id:
            item['quantity'] += 1
            break
    else:
        cart.append({
            "id": product['id'],
            "title": product['title'],
            "price": product['price'],
            "quantity": 1,
            "thumbnail": product['thumbnail']
        })
    print("--- ADD TO CART ---")
    print(f"User email: {session.get('email', 'ANONYMOUS')}")
    print(f"Added product ID: {product_id}")
    print(f"Current user_cart: {cart}")

    total_quantity = sum(i['quantity'] for i in cart)
    session['cart_count'] = total_quantity
    session.modified = True 

    return jsonify({"success": True, "cart_quantity": total_quantity})

@app.route('/add-quantity/<int:product_id>', methods=['POST'])
def add_quantity(product_id):
    cart = get_current_user_cart()
    updated_qty = 0
    for item in cart:
        if item['id'] == product_id:
            item['quantity'] += 1
            updated_qty = item['quantity']
            break
    
    total_qty = sum(i.get('quantity', 0) for i in cart)
    session['cart_count'] = total_qty
    session.modified = True
    
    return jsonify({"success": True, "quantity": updated_qty, "cart_quantity": total_qty})

@app.route('/subtract-quantity/<int:product_id>', methods=['POST'])
def subtract_quantity(product_id):
    cart = get_current_user_cart()
    updated_qty = 0
    for item in cart:
        if item['id'] == product_id and item['quantity'] > 1:
            item['quantity'] -= 1
            updated_qty = item['quantity']
            break
    
    total_qty = sum(i.get('quantity', 0) for i in cart)
    session['cart_count'] = total_qty
    session.modified = True
    
    return jsonify({"success": True, "quantity": updated_qty, "cart_quantity": total_qty})

@app.route('/remove-from-cart/<int:product_id>')
def remove_from_cart(product_id):
    # Použijeme logiku, která pozná, jestli mazat u usera nebo v session
    if 'email' in session:
        for user in registered_users:
            if user['email'] == session['email']:
                user['user_cart'] = [item for item in user['user_cart'] if item['id'] != product_id]
                break
    else:
        session['cart'] = [item for item in session.get('cart', []) if item['id'] != product_id]
    
    # Aktualizujeme globální počitadlo pro bublinu v navbaru
    cart = get_current_user_cart()
    session['cart_count'] = sum(item.get('quantity', 0) for item in cart)
    session.modified = True
    
    return redirect(url_for('shopping_cart'))

@app.route('/remove-from-cart-ajax/<int:product_id>', methods=['POST'])
def remove_from_cart_ajax(product_id):
    # 1. Logika smazání je stejná jako u klasické verze
    cart = []  # default to avoid UnboundLocalError if no user matches
    if 'email' in session:
        for user in registered_users:
            if user['email'] == session['email']:
                user['user_cart'] = [i for i in user['user_cart'] if i['id'] != product_id]
                cart = user['user_cart']
                break
    else:
        current_cart = session.get('cart') or []
        session['cart'] = [i for i in current_cart if i['id'] != product_id]
        session.modified = True
        cart = session['cart']
    print("--- REMOVE FROM MINI CART ---")
    print(f"User email: {session.get('email', 'ANONYMOUS')}")
    print(f"Removed product ID: {product_id}")
    print(f"Current user_cart: {cart}")
    
    # 2. Výpočet celkového množství (tady byla ta chyba s 'item')
    total_qty = sum(i.get('quantity', 0) for i in cart)
    session['cart_count'] = total_qty
    
    return jsonify({
        "success": True, 
        "cart_quantity": total_qty
    })


if __name__ == '__main__':
    app.run(debug=True)