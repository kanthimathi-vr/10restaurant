from django import forms

# This is a standard Django Form, NOT a Model.
class CheckoutForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        label="Your Name",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'John Doe'})
    )
    phone_number = forms.CharField(
        max_length=15,
        label="Phone Number",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '555-123-4567'})
    )