from flask import Blueprint, render_template, flash, send_from_directory, redirect,app, abort, url_for
from flask_login import login_required, current_user
from .forms import ShopItemsForm, OrderForm
from werkzeug.utils import secure_filename
from .models import Product, Order, Customer
from . import db
import logging

admin = Blueprint('admin', __name__)


@admin.route('/media/<path:filename>')
def get_image(filename):
    return send_from_directory('../media', filename)


@admin.route('/add-shop-items', methods=['GET', 'POST'])
@login_required
def add_shop_items():
    if current_user.id == 1:
        form = ShopItemsForm()

        if form.validate_on_submit():
            product_name = form.product_name.data
            author = form.author.data
            characteristic = form.characteristic.data
            previous_price = form.previous_price.data
            in_stock = form.in_stock.data
            category = form.category.data

            file = form.product_picture.data

            file_name = secure_filename(file.filename)

            file_path = f'./media/{file_name}'

            file.save(file_path)

            new_shop_item = Product()
            new_shop_item.product_name = product_name
            new_shop_item.author = author
            new_shop_item.characteristic = characteristic
            new_shop_item.previous_price = previous_price
            new_shop_item.in_stock = in_stock
            new_shop_item.category = category

            new_shop_item.product_picture = file_path

            try:
                db.session.add(new_shop_item)
                db.session.commit()
                flash(f'{product_name} added Successfully')
                print('Product Added')
                return render_template('add_shop_items.html', form=form)
            except Exception as e:
                print(e)
                flash('Product Not Added!!')

        return render_template('add_shop_items.html', form=form)

    return render_template('404.html')


@admin.route('/shop-items', methods=['GET', 'POST'])
@login_required
def shop_items():
    if current_user.id == 1:
        items = Product.query.order_by(Product.date_added).all()
        return render_template('shop_items.html', items=items)
    return render_template('404.html')


@admin.route('/update-item/<int:item_id>', methods=['GET', 'POST'])
@login_required
def update_item(item_id):
    if current_user.id == 1:
        form = ShopItemsForm()

        item_to_update = Product.query.get(item_id)

        form.product_name.render_kw = {'placeholder': item_to_update.product_name}
        form.author.render_kw = {'placeholder': item_to_update.author}
        form.characteristic.render_kw = {'placeholder': item_to_update.characteristic}
        form.previous_price.render_kw = {'placeholder': item_to_update.previous_price}
        form.in_stock.render_kw = {'placeholder': item_to_update.in_stock}
        form.category.render_kw = {'placeholder': item_to_update.category}

        if form.validate_on_submit():
            product_name = form.product_name.data
            author = form.author.data
            characteristic = form.characteristic.data
            previous_price = form.previous_price.data
            in_stock = form.in_stock.data
            category = form.category.data

            file = form.product_picture.data

            file_name = secure_filename(file.filename)
            file_path = f'./media/{file_name}'

            file.save(file_path)

            try:
                Product.query.filter_by(id=item_id).update(dict(product_name=product_name,
                                                                author = author,
                                                                characteristic = characteristic,
                                            
                                                                previous_price=previous_price,
                                                                in_stock=in_stock,
                                                                category=category,
                                                                product_picture=file_path))

                db.session.commit()
                flash(f'{product_name} updated Successfully')
                print('Product Upadted')
                return redirect('/shop-items')
            except Exception as e:
                print('Product not Upated', e)
                flash('Item Not Updated!!!')

        return render_template('update_item.html', form=form)
    return render_template('404.html')

@admin.route('/delete-item/<int:item_id>', methods=['GET', 'POST'])
@login_required
def delete_item(item_id):
    if current_user.id == 1:
        try:
            item_to_delete = Product.query.get(item_id)
            if item_to_delete:
                db.session.delete(item_to_delete)
                db.session.commit()
                flash('Товар успешно удалён', 'success')
            else:
                flash('Товар не найден', 'warning')
        except Exception as e:
            db.session.rollback()
            logging.error(f"Ошибка удаления товара {item_id}: {str(e)}") 
            flash(f'Ошибка: {str(e)}', 'error')
        return redirect('/shop-items')
    return render_template('404.html')


@admin.route('/view-orders')
@login_required
def view_orders():
    if current_user.id != 1:
        return render_template('404.html')
    
    orders = Order.query.all()
    form = OrderForm()  
    
    return render_template('view_orders.html', orders=orders, form=form)

@admin.route('/update-order/<int:order_id>', methods=['POST'])
@login_required
def update_order(order_id):
    if current_user.id != 1:
        abort(403)
    
    form = OrderForm()
    order = Order.query.get_or_404(order_id)
    
    if form.validate_on_submit():
        order.status = form.order_status.data
        try:
            db.session.commit()
            flash('Статус заказа обновлён!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Ошибка: ' + str(e), 'danger')
    
    return redirect(url_for('admin.view_orders'))


@admin.route('/customers')
@login_required
def display_customers():
    if current_user.id == 1:
        customers = Customer.query.all()
        return render_template('customers.html', customers=customers)
    return render_template('404.html')


@admin.route('/admin-page')
@login_required
def admin_page():
    if current_user.id == 1:
        return render_template('admin.html')
    return render_template('404.html')