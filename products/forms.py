from django import forms
from .models import Product


class ProductForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = [
            'name',
            'category',
            'description',
            'price',
            'discount_price',
            'stock',
            'condition',
            'image',
        ]

        widgets = {
            'description': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Describe your product'
            }),
            'price': forms.NumberInput(attrs={
                'placeholder': 'Enter product price'
            }),
            'discount_price': forms.NumberInput(attrs={
                'placeholder': 'Optional discount price'
            }),
            'stock': forms.NumberInput(attrs={
                'min': 0
            }),
        }