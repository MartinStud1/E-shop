from flask import Flask, render_template
import requests

app = Flask(__name__)


response = requests.get('https://dummyjson.com/products?limit=6')
      
data = response.json()
     
products = data.get('products', [])

@app.route('/')
def index():
    return render_template('index.html', products = products)

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
    return render_template('product.html')

@app.route('/product-detail')
def product_detail():
    return render_template('product-detail.html')

@app.route('/shopping-cart')
def shopping_cart():
    return render_template('shopping-cart.html')

if __name__ == '__main__':
    app.run(debug=True)