
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.utils.http import url_has_allowed_host_and_scheme

from .forms import CustomerRegistrationForm
from .models import CustomerProfile
from django.contrib.auth.decorators import login_required


def register(request):
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()
            CustomerProfile.objects.create(user=user)
            login(request, user)

            return redirect('home')
    else:
        form = CustomerRegistrationForm()

    return render(request, 'accounts/register.html', {
        'form': form
    })


def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)

            next_url = request.POST.get('next') or request.GET.get('next')

            if next_url and url_has_allowed_host_and_scheme(
                next_url,
                allowed_hosts={request.get_host()}
            ):
                return redirect(next_url)

            return redirect('home')
    else:
        form = AuthenticationForm()

    return render(request, 'accounts/login.html', {
        'form': form,
        'next': request.GET.get('next', '')
    })


def user_logout(request):
    logout(request)
    return redirect('home')

@login_required
def account_profile(request):
    profile, created = CustomerProfile.objects.get_or_create(
        user=request.user
    )

    return render(request, 'accounts/profile.html', {
        'profile': profile
    })
