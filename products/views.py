
from django.shortcuts import render, get_object_or_404
from .models import Product
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect
from django.utils.text import slugify
from sellers.models import SellerProfile
from .forms import ProductForm
from .models import Product, Category
from django.db.models import Avg, Count
from reviews.models import Review


def product_list(request, category_slug=None):
    products = Product.objects.filter(
        is_active=True
    ).select_related('category', 'seller')

    selected_category = None

    if category_slug:
        selected_category = get_object_or_404(
            Category,
            slug=category_slug,
            is_active=True
        )
        products = products.filter(category=selected_category)

    return render(request, 'products/product_list.html', {
        'products': products,
        'selected_category': selected_category
    })

    return render(request, 'products/product_list.html', {
        'products': products,
        'selected_category': selected_category
    })



from django.db.models import Avg, Count
from reviews.models import Review


def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.select_related('category', 'seller'),
        slug=slug,
        is_active=True
    )

    reviews = Review.objects.filter(
        product=product
    ).select_related('customer')

    rating_data = reviews.aggregate(
        average=Avg('rating'),
        count=Count('id')
    )

    user_review = None

    if request.user.is_authenticated:
        user_review = reviews.filter(
            customer=request.user
        ).first()

    context = {
        'product': product,
        'reviews': reviews,
        'average_rating': rating_data['average'] or 0,
        'review_count': rating_data['count'],
        'user_review': user_review,
        'review_submitted': request.GET.get('review_submitted') == '1',
    }

    return render(request, 'products/product_detail.html', context)

    return render(request, 'products/product_detail.html', {
        'product': product
    })


@login_required
def add_product(request):
    try:
        seller = request.user.seller_profile
    except SellerProfile.DoesNotExist:
        messages.error(request, 'You need a seller account first.')
        return redirect('seller_register')

    if seller.verification_status != 'approved' or not seller.is_active:
        messages.warning(request, 'Your store must be approved before adding products.')
        return redirect('home')

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)

        if form.is_valid():
            product = form.save(commit=False)
            product.seller = seller
            product.slug = slugify(product.name)

            base_slug = product.slug
            count = 1

            while Product.objects.filter(slug=product.slug).exists():
                product.slug = f'{base_slug}-{count}'
                count += 1

            product.save()

            messages.success(request, 'Product added successfully!')
            return redirect('product_list')
    else:
        form = ProductForm()

    return render(request, 'products/add_product.html', {
        'form': form
    })