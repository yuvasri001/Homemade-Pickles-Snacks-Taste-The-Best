from flask import Flask, render_template, request, redirect, url_for, session, flash
import os

app = Flask(__name__, static_folder='static')
app.secret_key = 'your_secret_key'

PRODUCTS = {
    'veg': [
        {'id': 'usirikaya', 'name': 'Usirikaya Pickle', 'prices': {'250g': 100, '500g': 170, '1kg': 300}, 'image': 'usirikaya.jpg'},
        {'id': 'aavakaya', 'name': 'Aavakaya Pickle', 'prices': {'250g': 110, '500g': 180, '1kg': 310}, 'image': 'aavakaya.jpg'},
        {'id': 'mirapakaya', 'name': 'Mirapakaya Pickle', 'prices': {'250g': 120, '500g': 190, '1kg': 320}, 'image': 'mirapakaya.jpg'},
        {'id': 'mango', 'name': 'Traditional Mango Pickle', 'prices': {'250g': 130, '500g': 200, '1kg': 330}, 'image': 'mango.jpg'},
        {'id': 'lemon', 'name': 'Zesty Lemon Pickle', 'prices': {'250g': 140, '500g': 210, '1kg': 340}, 'image': 'lemon.jpg'},
        {'id': 'tomato', 'name': 'Tomato Pickle', 'prices': {'250g': 150, '500g': 220, '1kg': 350}, 'image': 'tomato.jpg'}
    ],
    'nonveg': [
        {'id': 'chicken', 'name': 'Chicken Pickle', 'prices': {'250g': 160, '500g': 250, '1kg': 450}, 'image': 'chicken.jpg'},
        {'id': 'fish', 'name': 'Fish Pickle', 'prices': {'250g': 170, '500g': 260, '1kg': 460}, 'image': 'fish.jpg'},
        {'id': 'gongura_mutton', 'name': 'Gongura Mutton Pickle', 'prices': {'250g': 180, '500g': 270, '1kg': 470}, 'image': 'gongura_mutton.jpg'},
        {'id': 'mutton', 'name': 'Mutton Pickle', 'prices': {'250g': 190, '500g': 280, '1kg': 480}, 'image': 'mutton.jpg'},
        {'id': 'gongura_prawn', 'name': 'Gongura Prawn Pickle', 'prices': {'250g': 200, '500g': 290, '1kg': 490}, 'image': 'gongura_prawn.jpg'},
        {'id': 'gongura_chicken', 'name': 'Gongura Chicken Pickle', 'prices': {'250g': 210, '500g': 300, '1kg': 500}, 'image': 'gongura_chicken.jpg'}
    ],
    'snacks': [
        {'id': 'banana_chips', 'name': 'Banana Chips', 'prices': {'250g': 90, '500g': 160, '1kg': 280}, 'image': 'banana_chips.jpg'},
        {'id': 'aam_papad', 'name': 'Crispy Aam Papad', 'prices': {'250g': 95, '500g': 170, '1kg': 290}, 'image': 'aam_papad.jpg'},
        {'id': 'chekka_pakodi', 'name': 'Crispy Chekka Pakodi', 'prices': {'250g': 100, '500g': 180, '1kg': 300}, 'image': 'chekka_pakodi.jpg'},
        {'id': 'kaju_chikki', 'name': 'Kaju Chikki', 'prices': {'250g': 110, '500g': 190, '1kg': 310}, 'image': 'kaju_chikki.jpg'},
        {'id': 'peanut_chikki', 'name': 'Peanut Chikki', 'prices': {'250g': 120, '500g': 200, '1kg': 320}, 'image': 'peanut_chikki.jpg'},
        {'id': 'ravva_laddu', 'name': 'Ravva Laddu', 'prices': {'250g': 130, '500g': 210, '1kg': 330}, 'image': 'ravva_laddu.jpg'}
    ]
}

@app.route('/')
def welcome():
    return render_template('welcome.html')

@app.route('/home')
def index():
    return render_template('index.html', products=PRODUCTS)

@app.route('/veg')
def veg_pickles():
    return render_template('veg_pickles.html', products=PRODUCTS['veg'])

@app.route('/nonveg')
def non_veg_pickles():
    return render_template('non_veg_pickles.html', products=PRODUCTS['nonveg'])

@app.route('/snacks')
def snacks():
    return render_template('snacks.html', products=PRODUCTS['snacks'])

@app.route('/cart')
@app.route('/cart')
def cart():
    cart = session.get('cart', [])
    
    # Convert prices and quantities to int if they are strings
    for item in cart:
        item['price'] = float(item['price'])
        item['quantity'] = int(item['quantity'])

    return render_template('cart.html', cart=cart)

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    product_id = request.form.get('id')
    name = request.form.get('name')
    weight = request.form.get('weight')
    price = request.form.get('price')
    quantity = request.form.get('quantity')

    if not all([name, weight, price, quantity]):
        return "Missing form fields", 400

    price = float(price)
    quantity = int(quantity)

    item = {
        'id': product_id,
        'name': name,
        'weight': weight,
        'price': price,
        'quantity': quantity,
        'image': f'images/{product_id}.jpg'  # adjust this path if needed
    }

    if 'cart' not in session:
        session['cart'] = []

    # Check if item with same name & weight already in cart
    for existing_item in session['cart']:
        if existing_item['name'] == name and existing_item['weight'] == weight:
            existing_item['quantity'] += quantity
            break
    else:
        session['cart'].append(item)

    session.modified = True
    return redirect(url_for('cart'))

@app.route('/update_cart', methods=['POST'])
def update_cart():
    quantities = request.form.getlist('quantities[]')
    for i, qty in enumerate(quantities):
        session['cart'][i]['quantity'] = int(qty)
    session.modified = True
    return redirect(url_for('cart'))

@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    index = int(request.form['remove_index'])
    session['cart'].pop(index)
    session.modified = True
    return redirect(url_for('cart'))

@app.route('/apply_coupon', methods=['POST'])
def apply_coupon():
    code = request.form.get('coupon_code', '').strip()
    if 'cart' not in session:
        flash('No items in cart.', 'error')
        return redirect(url_for('cart'))

    discount = 0
    if code.lower() == 'save10':
        discount = 0.10
    elif code.lower() == 'save20':
        discount = 0.20
    else:
        flash('Invalid coupon code.', 'error')
        return redirect(url_for('cart'))

    for item in session['cart']:
        original_price = item['price']
        discounted_price = round(original_price * (1 - discount))
        item['price'] = discounted_price

    session.modified = True
    flash(f"Coupon applied! You saved {int(discount*100)}%.", "success")
    return redirect(url_for('cart'))

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    return render_template('checkout.html')

@app.route('/success', methods=['POST'])
def success():
    session.pop('cart', None)  # clear cart if needed
    return render_template('success.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.clear()  # This logs the user out
    return render_template('logout.html')  # Show logout confirmation page

@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html')

@app.route('/contact')
def contact():
    return render_template('contact_us.html')
@app.route('/update_quantity', methods=['POST'])
def update_quantity():
    index = int(request.form['index'])
    quantity = int(request.form['quantity'])

    if 'cart' in session:
        cart = session['cart']
        if 0 <= index < len(cart):
            cart[index]['quantity'] = quantity
            session['cart'] = cart
    return redirect(url_for('cart'))

if __name__ == '__main__':
    app.run(debug=True)
