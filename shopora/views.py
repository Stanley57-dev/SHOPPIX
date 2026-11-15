
from django.shortcuts import render
from products.models import Product, Category


def home(request):
    featured_products = Product.objects.filter(
        is_active=True,
        is_featured=True
    ).select_related('category', 'seller')[:8]

    latest_products = Product.objects.filter(
        is_active=True
    ).select_related('category', 'seller').order_by('-created_at')[:8]

    best_offer_products = Product.objects.filter(
        is_active=True,
        discount_price__isnull=False
    ).select_related('category', 'seller').order_by('-created_at')[:8]

    categories = Category.objects.filter(
        is_active=True,
        parent__isnull=True
    )[:6]

    context = {
        'featured_products': featured_products,
        'latest_products': latest_products,
        'best_offer_products': best_offer_products,
        'categories': categories,
    }

    return render(request, 'home.html', context)

