
import uuid
from datetime import date
from decimal import Decimal

import requests

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from products.models import Product
from .models import Order, OrderItem


PAYSTACK_URL = 'https://api.paystack.co'


def calculate_delivery_fee(city, state):
    city = city.strip().lower()
    state = state.strip().lower().replace(' state', '').strip()

    if state == 'ebonyi':
        if city == 'ishieke':
            return Decimal('1500.00')

        return Decimal('2500.00')

    return Decimal('3500.00')


@login_required
@require_http_methods(["GET", "POST"])
def checkout(request):

    cart = request.session.get('cart', {})

    if not cart:
        messages.warning(request, "Your shopping cart is empty.")
        return redirect('cart_detail')

    cart_items = []
    total = Decimal('0.00')

    # Get available products
    for product_id, quantity in cart.items():

        try:
            quantity = int(quantity)
        except (ValueError, TypeError):
            continue

        product = Product.objects.filter(
            id=product_id,
            is_active=True
        ).first()

        if product is None or quantity <= 0:
            continue

        if quantity > product.stock:
            messages.warning(
                request,
                f"Only {product.stock} unit(s) of {product.name} are available."
            )
            return redirect('cart_detail')

        price = product.discount_price or product.price
        subtotal = price * quantity
        total += subtotal

        cart_items.append({
            'product': product,
            'quantity': quantity,
            'price': price,
            'subtotal': subtotal,
        })

    if not cart_items:
        messages.warning(
            request,
            "Your cart has no available products."
        )
        return redirect('cart_detail')

    # Default values for checkout display
    delivery_fee = Decimal('0.00')
    grand_total = total

    if request.method == 'POST':

        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()
        city = request.POST.get('city', '').strip()
        state = request.POST.get('state', '').strip()

        requested_date = request.POST.get(
            'requested_delivery_date', ''
        ).strip()

        if not all([
            full_name,
            email,
            phone,
            address,
            city,
            state,
            requested_date
        ]):
            messages.error(
                request,
                "Please complete all delivery details, including your preferred delivery date."
            )
            return redirect('checkout')

        try:
            requested_delivery_date = date.fromisoformat(
                requested_date
            )
        except ValueError:
            messages.error(
                request,
                "Please select a valid delivery date."
            )
            return redirect('checkout')

        if requested_delivery_date < timezone.localdate():
            messages.error(
                request,
                "Your preferred delivery date cannot be in the past."
            )
            return redirect('checkout')

        # Calculate delivery fee
        delivery_fee = calculate_delivery_fee(city, state)

        # Calculate final amount
        grand_total = total + delivery_fee

        # Check Paystack configuration
        secret_key = settings.PAYSTACK_SECRET_KEY

        if not secret_key:
            messages.error(
                request,
                "Payment configuration is incomplete."
            )
            return redirect('checkout')

        # Create payment reference
        reference = uuid.uuid4().hex

        # Create order
        order = Order.objects.create(
            customer=request.user,
            full_name=full_name,
            email=email,
            phone=phone,
            address=address,
            city=city,
            state=state,
            total_amount=grand_total,
            delivery_fee=delivery_fee,
            payment_reference=reference,
            requested_delivery_date=requested_delivery_date,
        )

        # Create order items
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                product_name=item['product'].name,
                price=item['price'],
                quantity=item['quantity'],
            )

        # Paystack callback URL
        callback_url = request.build_absolute_uri(
            reverse('payment_callback')
        )

        # Initialize payment with product total + delivery fee
        payment_data = {
            'email': email,
            'amount': int(grand_total * 100),
            'currency': 'NGN',
            'reference': reference,
            'callback_url': callback_url,
        }

        headers = {
            'Authorization': f'Bearer {secret_key}',
            'Content-Type': 'application/json',
        }

        try:
            response = requests.post(
                f'{PAYSTACK_URL}/transaction/initialize',
                json=payment_data,
                headers=headers,
                timeout=30,
            )

            response.raise_for_status()
            result = response.json()

            if result.get('status') is True:
                authorization_url = result['data']['authorization_url']
                return redirect(authorization_url)

            messages.error(
                request,
                "Paystack could not initialize your payment. Please try again."
            )

        except (requests.RequestException, ValueError, KeyError):
            messages.error(
                request,
                "Unable to connect to Paystack. Please try again."
            )

        return redirect('checkout')

    # Display checkout page
    return render(request, 'orders/checkout.html', {
        'cart_items': cart_items,
        'total': total,
        'delivery_fee': delivery_fee,
        'grand_total': grand_total,
    })


@login_required
def payment_callback(request):

    reference = request.GET.get('reference')

    if not reference:
        messages.error(
            request,
            "Payment reference was not provided."
        )
        return redirect('cart_detail')

    order = get_object_or_404(
        Order,
        payment_reference=reference,
        customer=request.user
    )

    if order.payment_status == 'paid':
        return redirect('order_success', order_id=order.id)

    secret_key = settings.PAYSTACK_SECRET_KEY

    if not secret_key:
        messages.error(
            request,
            "Payment verification is unavailable."
        )
        return redirect('checkout')

    headers = {
        'Authorization': f'Bearer {secret_key}',
    }

    # Verify payment with Paystack
    try:
        response = requests.get(
            f'{PAYSTACK_URL}/transaction/verify/{reference}',
            headers=headers,
            timeout=30,
        )

        response.raise_for_status()
        result = response.json()

        payment = result.get('data', {})

        payment_verified = (
            result.get('status') is True
            and payment.get('status') == 'success'
            and payment.get('reference') == reference
            and payment.get('amount') == int(order.total_amount * 100)
            and payment.get('currency') == 'NGN'
        )

        if payment_verified:

            order.payment_status = 'paid'
            order.status = 'confirmed'

            order.save(update_fields=[
                'payment_status',
                'status',
                'updated_at',
            ])

            # Clear cart after successful payment
            request.session['cart'] = {}
            request.session.modified = True

            messages.success(
                request,
                "Payment successful! Your order is confirmed."
            )

            return redirect(
                'order_success',
                order_id=order.id
            )

        messages.error(
            request,
            "Payment was not successful or could not be verified. "
            "Your order remains unpaid."
        )

    except (requests.RequestException, ValueError):
        messages.error(
            request,
            "We could not verify your payment. Please try again."
        )

    return redirect('checkout')


@login_required
def order_success(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id,
        customer=request.user
    )

    return render(request, 'orders/order_success.html', {
        'order': order,
    })


@login_required
def my_orders(request):

    orders = Order.objects.filter(
        customer=request.user
    ).prefetch_related('items').order_by('-created_at')

    return render(request, 'orders/my_orders.html', {
        'orders': orders,
    })


@login_required
def order_detail(request, order_id):

    order = get_object_or_404(
        Order.objects.prefetch_related('items'),
        id=order_id,
        customer=request.user
    )

    return render(request, 'orders/order_detail.html', {
        'order': order,
    })
