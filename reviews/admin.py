
from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        'product',
        'customer',
        'rating',
        'title',
        'created_at',
    )

    list_filter = ('rating', 'created_at')
    search_fields = (
        'product__name',
        'customer__username',
        'title',
        'comment',
    )

    readonly_fields = ('created_at', 'updated_at')
