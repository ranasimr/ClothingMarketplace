from django import forms
from .models import Order

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'phone', 'email', 'address_line_1', 'address_line_2', 'country', 'state', 'city', 'order_note']

    def clean_phone(self):
        phone_number = self.cleaned_data.get('phone')
        if phone_number:
            if not phone_number.isdigit():
                raise forms.ValidationError("Phone number must contain only digits.")
            elif len(phone_number) != 10:
                raise forms.ValidationError("Phone number must be exactly 10 digits long.")
        return phone_number

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if first_name and not first_name.replace(" ", "").isalpha():
            raise forms.ValidationError("First name must contain only alphabetic characters.")
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if last_name and not last_name.replace(" ", "").isalpha():
            raise forms.ValidationError("Last name must contain only alphabetic characters.")
        return last_name
    
    def clean_address_line_1(self):
        address_line_1 = self.cleaned_data.get('address_line_1')
        if address_line_1 and len(address_line_1.split()) > 50:
            raise forms.ValidationError("Address line 1 can only contain up to 50 words.")
        # Add validation for alphanumeric characters and specific symbols here
        if address_line_1 and not all(char.isalnum() or char in ' /\\,#' for char in address_line_1):
            raise forms.ValidationError("Address line 1 can only contain alphanumeric characters and /\\,# symbols.")
        return address_line_1

    def clean_address_line_2(self):
        address_line_2 = self.cleaned_data.get('address_line_2')
        if address_line_2 and len(address_line_2.split()) > 50:
            raise forms.ValidationError("Address line 2 can only contain up to 50 words.")
        # Add validation for alphanumeric characters and specific symbols here
        if address_line_2 and not all(char.isalnum() or char in ' /\\,#' for char in address_line_2):
            raise forms.ValidationError("Address line 2 can only contain alphanumeric characters and /\\,# symbols.")
        return address_line_2

    def clean_country(self):
        country = self.cleaned_data.get('country')
        if country and not country.isalpha():
            raise forms.ValidationError("Country must contain only alphabetic characters.")
        return country

    def clean_state(self):
        state = self.cleaned_data.get('state')
        if state and not state.isalpha():
            raise forms.ValidationError("State must contain only alphabetic characters.")
        return state

    def clean_city(self):
        city = self.cleaned_data.get('city')
        if city and not city.isalpha():
            raise forms.ValidationError("City must contain only alphabetic characters.")
        return city

    def __init__(self, *args, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['placeholder'] = 'Enter First Name'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Enter Last Name'
        self.fields['phone'].widget.attrs['placeholder'] = 'Enter Phone Number'
        self.fields['email'].widget.attrs['placeholder'] = 'Enter Email Address'
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
