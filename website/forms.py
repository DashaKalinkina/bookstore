from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, FloatField, PasswordField, EmailField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, length, NumberRange
from flask_wtf.file import FileField, FileRequired


class SignUpForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired(), length(min=2)])
    password1 = PasswordField('Enter Your Password', validators=[DataRequired(), length(min=6)])
    password2 = PasswordField('Confirm Your Password', validators=[DataRequired(), length(min=6)])
    submit = SubmitField('Зарегистрироваться')


class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired()])
    password = PasswordField('Enter Your Password', validators=[DataRequired()])
    submit = SubmitField('Войти')


class PasswordChangeForm(FlaskForm):
    current_password = PasswordField('Введите старый пароль', validators=[DataRequired(), length(min=6)])
    new_password = PasswordField('Новый пароль', validators=[DataRequired(), length(min=6)])
    confirm_new_password = PasswordField('Повторите пароль', validators=[DataRequired(), length(min=6)])
    change_password = SubmitField('Изменить пароль')


class ShopItemsForm(FlaskForm):
    product_name = StringField('Name of Product', validators=[DataRequired()])
    author = StringField('Name of author', validators=[DataRequired()])
    characteristic = StringField('Characteristic', validators=[DataRequired()])
    previous_price = FloatField('Previous Price', validators=[DataRequired()])
    in_stock = IntegerField('In Stock', validators=[DataRequired(), NumberRange(min=0)])
    product_picture = FileField('Product Picture', validators=[DataRequired()])
    category = SelectField('Category', choices=[
        ('Популярное', 'Популярное'),
        ('Романы', 'Романы'),
        ('Детективы', 'Детективы'),
        ('Фэнтези', 'Фэнтези'),
        ('Искусство', 'Искусство'),
        ('Психология', 'Психология'),
        ('Приключения', 'Приключения')
    ])
    add_product = SubmitField('Add Product')
    update_product = SubmitField('Update')



class OrderForm(FlaskForm):
    order_status = SelectField(
        'Статус',
        choices=[
            ('В обработке', 'В обработке'),
            ('Отправлен', 'Отправлен'),
            ('Доставлен', 'Доставлен'),
            ('Отменён', 'Отменён')
        ],
        validators=[DataRequired()]
    )
    submit = SubmitField('Обновить')