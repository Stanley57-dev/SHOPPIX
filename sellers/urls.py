
from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.seller_register, name='seller_register'),
]
