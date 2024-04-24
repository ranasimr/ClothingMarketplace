from typing import Any, Mapping
from django import forms
from django.core.files.base import File
from django.db.models.base import Model
from django.forms.utils import ErrorList
from .models import Account,UserProfile
from django.core.exceptions import ValidationError
from .models import Address

import logging 
logger = logging.getLogger(__name__)

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder':'Enter Password',
        'class':'form-control',
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder':'confirm Password'
    }))
   
    class Meta:
        model =Account
        fields = ['first_name','last_name','phone_number','email','password']



    def __init__(self,*args,**kwargs):
        super(RegistrationForm,self).__init__(*args,**kwargs)  
        self.fields['first_name'].widget.attrs['placeholder']='Enter First Name'
        self.fields['last_name'].widget.attrs['placeholder']='Enter Last Name'
        self.fields['phone_number'].widget.attrs['placeholder']='Enter Phone Number'
        self.fields['email'].widget.attrs['placeholder']='Enter Email Address' 
        for field in self.fields:
            self.fields[field].widget.attrs['class']='form-control'


    # def clean(self):
    #     cleaned_data= super(RegistrationForm,self).clean()
    #     password= cleaned_data.get('password')
    #     confirm_password= cleaned_data.get('confirm_password')

    #     if password != confirm_password:
    #          raise forms.ValidationError(
    #              "Password does not match!"
    #          )
    def clean(self):
        cleaned_data = super().clean()

        print("Clean method called")
        print("Password:", cleaned_data.get('password'))
        print("Confirm Password:", cleaned_data.get('confirm_password'))
        print("Phone Number:", cleaned_data.get('phone_number'))
        print("First Name:", cleaned_data.get('first_name'))
        print("Last Name:", cleaned_data.get('last_name'))

        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        phone_number = cleaned_data.get('phone_number')
        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')

        if password and confirm_password and password != confirm_password:
          raise forms.ValidationError("Password does not match!")

       
        if phone_number:
           if not phone_number.isdigit():
              raise forms.ValidationError("Phone number must contain only digits.")
           elif len(phone_number) != 10:
              raise forms.ValidationError("Phone number must be exactly 10 digits long.")

        if first_name and not first_name.replace(" ", "").isalpha():  # Handle spaces
          raise forms.ValidationError( "First name must contain only alphabetic characters.")

        if last_name and not last_name.replace(" ", "").isalpha():  # Handle spaces
          raise forms.ValidationError( "Last name must contain only alphabetic characters.")
        


class UserForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ('first_name', 'last_name', 'phone_number')

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if not first_name.isalpha() or len(first_name) > 10:
            raise forms.ValidationError("First name must contain only alphabetic characters and be at most 10 characters long.")
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if not last_name.isalpha() or len(last_name) > 10:
            raise forms.ValidationError("Last name must contain only alphabetic characters and be at most 10 characters long.")
        return last_name

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if not phone_number.isdigit() or len(phone_number) != 10:
            raise forms.ValidationError("Phone number must contain only digits and be exactly 10 digits long.")
        return phone_number

class UserProfileForm(forms.ModelForm):
    profile_picture = forms.ImageField(required=False, error_messages = {'invalid':("Image files only")}, widget=forms.FileInput)
    class Meta:
        model = UserProfile
        fields = ('phone_number','address_line_1', 'address_line_2', 'city', 'state', 'country', 'profile_picture')

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'   
    
    
    def clean_profile_picture(self):
        profile_picture = self.cleaned_data.get('profile_picture')
        if profile_picture:
            # Get the file extension
            ext = profile_picture.name.split('.')[-1].lower()
            logger.debug("File extension: %s", ext)
            # Allowed extensions for image files
            allowed_extensions = ['jpg', 'jpeg', 'png']
            if ext not in allowed_extensions:
                logger.error("Invalid file format: %s", ext)
                raise ValidationError("Only JPG, JPEG and PNG files are allowed.")
        return profile_picture
    
    def clean_address_line_1(self):
        address_line_1 = self.cleaned_data.get('address_line_1')
        if address_line_1 and len(address_line_1.split()) > 50:
            raise forms.ValidationError("Address line 1 can only contain up to 50 words.")
        # Add validation for alphanumeric characters and specific symbols here
        if address_line_1 and not all(char.isalnum() or char in ' /\\,.#' for char in address_line_1):
            raise forms.ValidationError("Address line 1 can only contain alphanumeric characters and /\\,.# symbols.")
        return address_line_1

    def clean_address_line_2(self):
        address_line_2 = self.cleaned_data.get('address_line_2')
        if address_line_2 and len(address_line_2.split()) > 50:
            raise forms.ValidationError("Address line 2 can only contain up to 50 words.")
        # Add validation for alphanumeric characters and specific symbols here
        if address_line_2 and not all(char.isalnum() or char in ' /\\,.#' for char in address_line_2):
            raise forms.ValidationError("Address line 2 can only contain alphanumeric characters and /\\,.# symbols.")
        return address_line_2


    def clean_city(self):
        city = self.cleaned_data.get('city')
        if not city.isalpha() or len(city) > 20:
            raise forms.ValidationError("City must contain only alphabetic characters and be at most 20 characters long.")
        return city

    def clean_state(self):
        state = self.cleaned_data.get('state')
        if not state.isalpha() or len(state) > 20:
            raise forms.ValidationError("State must contain only alphabetic characters and be at most 20 characters long.")
        return state

    def clean_country(self):
        country = self.cleaned_data.get('country')
        if not country.isalpha() or len(country) > 20:
            raise forms.ValidationError("Country must contain only alphabetic characters and be at most 20 characters long.")
        return country 



# class AddressForm(forms.ModelForm):
#     class Meta:
#         model = Address
#         fields = ['address_line_1', 'address_line_2', 'city', 'state', 'country']

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['address_line_1', 'address_line_2', 'city', 'state', 'country']

    def __init__(self, *args, **kwargs):
        super(AddressForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'   

    def clean_address_line_1(self):
        address_line_1 = self.cleaned_data.get('address_line_1')
        if address_line_1 and len(address_line_1.split()) > 50:
            raise forms.ValidationError("Address line 1 can only contain up to 50 words.")
        # Add validation for alphanumeric characters and specific symbols here
        if address_line_1 and not all(char.isalnum() or char in ' /\\,.#' for char in address_line_1):
            raise forms.ValidationError("Address line 1 can only contain alphanumeric characters and /\\,.# symbols.")
        return address_line_1

    def clean_address_line_2(self):
        address_line_2 = self.cleaned_data.get('address_line_2')
        if address_line_2 and len(address_line_2.split()) > 50:
            raise forms.ValidationError("Address line 2 can only contain up to 50 words.")
        # Add validation for alphanumeric characters and specific symbols here
        if address_line_2 and not all(char.isalnum() or char in ' /\\,.#' for char in address_line_2):
            raise forms.ValidationError("Address line 2 can only contain alphanumeric characters and /\\,.# symbols.")
        return address_line_2

    def clean_city(self):
        city = self.cleaned_data.get('city')
        if not city.isalpha() or len(city) > 20:
            raise forms.ValidationError("City must contain only alphabetic characters and be at most 20 characters long.")
        return city

    def clean_state(self):
        state = self.cleaned_data.get('state')
        if not state.isalpha() or len(state) > 20:
            raise forms.ValidationError("State must contain only alphabetic characters and be at most 20 characters long.")
        return state

    def clean_country(self):
        country = self.cleaned_data.get('country')
        if not country.isalpha() or len(country) > 20:
            raise forms.ValidationError("Country must contain only alphabetic characters and be at most 20 characters long.")
        return country  





