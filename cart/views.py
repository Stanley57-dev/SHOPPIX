
from decimal import Decimal

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST

from products.models import Product


def get_cart(request):
    return request.session.get('cart', {})


def cart_detail(request):
    cart = get_cart(request)
    cart_items = []
    total = Decimal('0.00')

    for product_id, quantity in cart.items():
        product = Product.objects.filter(
            id=product_id,
            is_active=True
        ).first()

        if product is None:
            continue

        quantity = min(int(quantity), product.stock)

        if quantity <= 0:
            continue

        price = product.discount_price or product.price
        subtotal = price * quantity
        total += subtotal

        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal,
        })

    return render(request, 'cart/cart_detail.html', {
        'cart_items': cart_items,
        'total': total,
    })


@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(
        Product,
        id=product_id,
        is_active=True
    )

    cart = get_cart(request)
    product_id = str(product.id)

    quantity = int(cart.get(product_id, 0))

    if quantity < product.stock:
        cart[product_id] = quantity + 1
        request.session['cart'] = cart
        request.session.modified = True
        messages.success(request, 'Product added to your cart!')
    else:
        messages.warning(request, 'Sorry, this product is out of stock.')

    return redirect('cart_detail')


@require_POST
def update_cart(request, product_id):
    product = get_object_or_404(
        Product,
        id=product_id,
        is_active=True
    )

    cart = get_cart(request)
    product_id = str(product.id)

    try:
        quantity = int(request.POST.get('quantity', 1))
    except (ValueError, TypeError):
        quantity = 1

    if quantity <= 0:
        cart.pop(product_id, None)
    elif quantity <= product.stock:
        cart[product_id] = quantity
    else:
        messages.warning(request, 'Requested quantity exceeds available stock.')

    request.session['cart'] = cart
    request.session.modified = True

    return redirect('cart_detail')


@require_POST
def remove_from_cart(request, product_id):
    cart = get_cart(request)
    cart.pop(str(product_id), None)

    request.session['cart'] = cart
    request.session.modified = True

    messages.success(request, 'Product removed from your cart.')

    return redirect('cart_detail')
