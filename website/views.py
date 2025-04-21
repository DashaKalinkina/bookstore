from flask import Blueprint, render_template, flash, redirect, request, jsonify
from .models import Product, Cart, Order
from flask_login import login_required, current_user
from . import db


views = Blueprint('views', __name__)


@views.route('/')
def home():
    items = Product.query.filter_by(category='Популярное').all()
    categories = ['Романы', 'Детективы', 'Фэнтези', 'Искусство', 'Психология', 'Приключения','Популярное']
    return render_template('home.html', items=items, categories=categories,
                           cart=Cart.query.filter_by(customer_link=current_user.id).all()
                           if current_user.is_authenticated else [])

@views.route('/category/<string:category_name>')
def category(category_name):
    items = Product.query.filter_by(category=category_name).all()
    
    return render_template('category.html', items=items, category_name=category_name,
                           cart=Cart.query.filter_by(customer_link=current_user.id).all()
                           if current_user.is_authenticated else [])

@views.route('/characteristic/<int:book_id>')
def book_detail(book_id):
    item = Product.query.get_or_404(book_id)
    return render_template('characteric.html', 
                           cart=Cart.query.filter_by(customer_link=current_user.id).all()
                           if current_user.is_authenticated else [],item=item)
@views.route('/sert')
def sertificate():
    return render_template('sertificat.html', 
                           cart=Cart.query.filter_by(customer_link=current_user.id).all()
                           if current_user.is_authenticated else [])


@views.route('/rasp')
def rasp():
    return render_template('2.html', 
                           cart=Cart.query.filter_by(customer_link=current_user.id).all()
                           if current_user.is_authenticated else [])

@views.route('/popular')
def popular():
    items = Product.query.all()
    categories = ['Романы', 'Детективы', 'Фэнтези', 'Искусство', 'Психология', 'Приключения']
    return render_template('3.html', items=items, categories=categories,
                           cart=Cart.query.filter_by(customer_link=current_user.id).all()
                           if current_user.is_authenticated else [])


@views.route('/add-to-cart/<int:item_id>')
@login_required
def add_to_cart(item_id):
    item_to_add = Product.query.get(item_id)
    item_exists = Cart.query.filter_by(product_link=item_id, customer_link=current_user.id).first()
    if item_exists:
        try:
            item_exists.quantity = item_exists.quantity + 1
            db.session.commit()
            flash(f' Quantity of { item_exists.product.product_name } has been updated')
            return redirect(request.referrer)
        except Exception as e:
            print('Quantity not Updated', e)
            flash(f'Quantity of { item_exists.product.product_name } not updated')
            return redirect(request.referrer)

    new_cart_item = Cart()
    new_cart_item.quantity = 1
    new_cart_item.product_link = item_to_add.id
    new_cart_item.customer_link = current_user.id

    try:
        db.session.add(new_cart_item)
        db.session.commit()
        flash(f'{new_cart_item.product.product_name} added to cart')
    except Exception as e:
        print('Item not added to cart', e)
        flash(f'{new_cart_item.product.product_name} has not been added to cart')

    return redirect(request.referrer)


@views.route('/cart')
@login_required
def show_cart():
    cart = Cart.query.filter_by(customer_link=current_user.id).all()
    amount = 0
    for item in cart:
        amount += item.product.previous_price * item.quantity 

    return render_template('cart.html', cart=cart, amount=amount, total=amount+200)

@views.route('/pluscart')
@login_required
def plus_cart():
    try:
        cart_id = request.args.get('cart_id')
        cart_item = Cart.query.get(cart_id)
        if not cart_item:
            return jsonify({'error': 'Item not found'}), 404
            
        cart_item.quantity += 1
        db.session.commit()

        cart = Cart.query.filter_by(customer_link=current_user.id).all()
        amount = sum(item.product.previous_price * item.quantity for item in cart)

        return jsonify({
            'quantity': cart_item.quantity,
            'amount': amount,
            'total': amount + 200
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@views.route('/minuscart')
@login_required
def minus_cart():
    try:
        cart_id = request.args.get('cart_id')
        cart_item = Cart.query.get(cart_id)
        if not cart_item:
            return jsonify({'error': 'Item not found'}), 404
            
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            db.session.commit()

        cart = Cart.query.filter_by(customer_link=current_user.id).all()
        amount = sum(item.product.previous_price * item.quantity for item in cart)

        return jsonify({
            'quantity': cart_item.quantity,
            'amount': amount,
            'total': amount + 200
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@views.route('/removecart')
@login_required
def remove_cart():
    try:
        cart_id = request.args.get('cart_id')
        cart_item = Cart.query.get(cart_id)
        if not cart_item:
            return jsonify({'error': 'Item not found'}), 404
            
        db.session.delete(cart_item)
        db.session.commit()

        cart = Cart.query.filter_by(customer_link=current_user.id).all()
        amount = sum(item.product.previous_price * item.quantity for item in cart)

        return jsonify({
            'quantity': 0,
            'amount': amount,
            'total': amount + 200
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    
@views.route('/place-order', methods=['POST'])
@login_required
def place_order():

    customer_name = request.form.get('customer_name')
    customer_phone = request.form.get('customer_phone')
    customer_address = request.form.get('customer_address')
    customer_comment = request.form.get('customer_comment', '')


    if not all([customer_name, customer_phone, customer_address]):
        flash('Please fill all required fields')
        return redirect('/cart')

    customer_cart = Cart.query.filter_by(customer_link=current_user.id).all()
    if not customer_cart:
        flash('Your cart is empty')
        return redirect('/')

    try:
        
        total = 0
        order_items = []
        
        for item in customer_cart:
            product = Product.query.get(item.product_link)
            if product.in_stock < item.quantity:
                flash(f'Not enough stock for {product.product_name}')
                return redirect('/cart')
            
            total += product.previous_price * item.quantity
            order_items.append({
                'product': product,
                'quantity': item.quantity,
                'price': product.previous_price
            })


        for item in order_items:
            new_order = Order(
                quantity=item['quantity'],
                price=item['price'],
                product_link=item['product'].id,
                customer_link=current_user.id,
                customer_name=customer_name,
                customer_phone=customer_phone,
                customer_address=customer_address,
                customer_comment=customer_comment,
                status='В обработке'
            )
            db.session.add(new_order)
            item['product'].in_stock -= item['quantity']
            Cart.query.filter_by(id=item['product'].id).delete()

        db.session.commit()
        flash('Order placed successfully!')
        return redirect('/orders')
        
    except Exception as e:
        db.session.rollback()
        print(f"Error: {e}")
        flash('Failed to place order. Please try again.')
        return redirect('/cart')

@views.route('/orders')
@login_required
def order():
    orders = Order.query.filter_by(customer_link=current_user.id).all()
    return render_template('orders.html', orders=orders)


@views.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_query = request.form.get('search')
        items = Product.query.filter(Product.product_name.ilike(f'%{search_query}%')).all()
        return render_template('search.html', items=items, cart=Cart.query.filter_by(customer_link=current_user.id).all()
                           if current_user.is_authenticated else [])

    return render_template('search.html')












