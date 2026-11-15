
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import SellerRegistrationForm
from .models import SellerProfile


@login_required
def seller_register(request):

    # Check whether the user already has a seller profile
    if hasattr(request.user, 'seller_profile'):
        messages.info(request, 'You have already submitted a seller application.')
        return redirect('home')

    if request.method == 'POST':
        form = SellerRegistrationForm(request.POST, request.FILES)

        if form.is_valid():
            seller = form.save(commit=False)
            seller.user = request.user
            seller.save()

            messages.success(
                request,
                'Your seller application has been submitted successfully. '
                'Please wait for admin approval.'
            )

            return redirect('home')

    else:
        form = SellerRegistrationForm()

    return render(request, 'sellers/register.html', {
        'form': form
    })
