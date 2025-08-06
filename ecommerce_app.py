import os
import django
from django.conf import settings
from django.db import models
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import path

# ---------------- SETTINGS ----------------
BASE_DIR = os.path.dirname(__file__)
settings.configure(
    DEBUG=True,
    SECRET_KEY='secretkey123',
    ROOT_URLCONF=__name__,
    ALLOWED_HOSTS=['*'],
    INSTALLED_APPS=[
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.staticfiles',
        __name__,
    ],
    MIDDLEWARE=[
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
    ],
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    },
    STATIC_URL='/static/',
    TEMPLATES=[{
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
    }],
)

django.setup()

# ---------------- MODELS ----------------
class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    def __str__(self):
        return self.name

class Order(models.Model):
    items = models.TextField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

# ---------------- VIEWS ----------------
def home(request):
    products = Product.objects.all()
    html = "<h1>My E-commerce Store</h1>"
    for p in products:
        html += f"<p><a href='/product/{p.id}/'>{p.name}</a> - ${p.price}</p>"
    html += "<p><a href='/cart/'>View Cart</a></p>"
    return HttpResponse(html)

def product_detail(request, id):
    product = Product.objects.get(id=id)
    html = f"<h1>{product.name}</h1><p>{product.description}</p><p>${product.price}</p>"
    html += f"<a href='/add_to_cart/{product.id}/'>Add to Cart</a> | <a href='/'>Back</a>"
    return HttpResponse(html)

def add_to_cart(request, id):
    cart = request.session.get('cart', [])
    cart.append(id)
    request.session['cart'] = cart
    return redirect('/cart/')

def view_cart(request):
    cart = request.session.get('cart', [])
    products = Product.objects.filter(id__in=cart)
    total = sum([p.price for p in products])
    html = "<h1>Your Cart</h1>"
    for p in products:
        html += f"<p>{p.name} - ${p.price}</p>"
    html += f"<p>Total: ${total}</p>"
    html += "<a href='/checkout/'>Checkout</a>"
    return HttpResponse(html)

def checkout(request):
    cart = request.session.get('cart', [])
    products = Product.objects.filter(id__in=cart)
    total = sum([p.price for p in products])
    Order.objects.create(items=", ".join([p.name for p in products]), total_price=total)
    request.session['cart'] = []
    return HttpResponse(f"<h1>Order Placed!</h1><p>Total Paid: ${total}</p><a href='/'>Back to Store</a>")

# ---------------- URLS ----------------
urlpatterns = [
    path('', home),
    path('product/<int:id>/', product_detail),
    path('add_to_cart/<int:id>/', add_to_cart),
    path('cart/', view_cart),
    path('checkout/', checkout),
]

# ---------------- INIT DATABASE ----------------
if __name__ == "__main__":
    from django.core.management import execute_from_command_line
    if not os.path.exists(os.path.join(BASE_DIR, 'db.sqlite3')):
        execute_from_command_line(['', 'makemigrations', __name__])
        execute_from_command_line(['', 'migrate'])
        # Add sample products
        Product.objects.create(name="Laptop", price=500, description="A fast laptop")
        Product.objects.create(name="Phone", price=300, description="A smartphone")
        Product.objects.create(name="Headphones", price=50, description="Noise cancelling")
    execute_from_command_line(['', 'runserver'])
