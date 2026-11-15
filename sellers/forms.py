from django import forms
from .models import SellerProfile


class SellerRegistrationForm(forms.ModelForm):

    class Meta:
        model = SellerProfile
        fields = [
            'store_name',
            'description',
            'phone',
            'address',
        ]

        widgets = {
            'store_name': forms.TextInput(attrs={
                'placeholder': 'Enter your store name'
            }),
            'description': forms.Textarea(attrs={
                'placeholder': 'Tell customers about your store',
                'rows': 4
            }),
            'phone': forms.TextInput(attrs={
                'placeholder': 'Enter your phone number'
            }),
            'address': forms.Textarea(attrs={
                'placeholder': 'Enter your business address',
                'rows': 3
            }),
        }