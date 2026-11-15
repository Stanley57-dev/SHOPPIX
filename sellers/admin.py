from django.contrib import admin
from .models import SellerProfile


@admin.register(SellerProfile)
class SellerProfileAdmin(admin.ModelAdmin):
    list_display = (
        'store_name',
        'user',
        'phone',
        'verification_status',
        'is_active',
        'created_at'
    )

    search_fields = ('store_name', 'user__username', 'phone')

    list_filter = (
        'verification_status',
        'is_active'
    )

    prepopulated_fields = {'slug': ('store_name',)}