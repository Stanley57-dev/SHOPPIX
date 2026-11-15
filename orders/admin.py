
from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product_name', 'price', 'quantity', 'subtotal')

    def subtotal(self, obj):
        return obj.subtotal

    subtotal.short_description = 'Subtotal'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        'order_number',
        'customer',
        'full_name',
        'total_amount',
        'status',
        'payment_status',
        'requested_delivery_date',
        'requested_delivery_status',
        'estimated_delivery_date',
        'actual_delivery_date',
        'created_at',
    )

    list_filter = (
    'status',
    'payment_status',
    'requested_delivery_status',
    'created_at',
    )
    search_fields = (
        'order_number',
        'full_name',
        'email',
        'phone',
    )

    readonly_fields = (
        'order_number',
        'payment_reference',
        'customer',
        'total_amount',
        'created_at',
        'updated_at',
    )

    inlines = [OrderItemInline]

    list_per_page = 20
