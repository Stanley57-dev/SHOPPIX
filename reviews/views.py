
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse

from products.models import Product
from .models import Review
from .forms import ReviewForm


@login_required
def add_review(request, product_id):
    product = get_object_or_404(
        Product,
        id=product_id,
        is_active=True
    )

    existing_review = Review.objects.filter(
        product=product,
        customer=request.user
    ).first()

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=existing_review)

        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.customer = request.user
            review.save()

            messages.success(
                request,
                'Thank you for sharing your experience!'
            )

            return redirect(
                reverse('product_detail', kwargs={'slug': product.slug})
                + '?review_submitted=1'
            )
        else:
            messages.error(
                request,
                'Please correct the errors below and try again.'
            )
    else:
        form = ReviewForm(instance=existing_review)

    return render(request, 'reviews/add_review.html', {
        'form': form,
        'product': product,
    })


@login_required
def delete_review(request, review_id):
    review = get_object_or_404(
        Review,
        id=review_id,
        customer=request.user
    )

    if request.method == 'POST':
        product_slug = review.product.slug
        review.delete()

        messages.success(request, 'Your review has been deleted!')

        return redirect('product_detail', slug=product_slug)

    return redirect('product_detail', slug=review.product.slug)
