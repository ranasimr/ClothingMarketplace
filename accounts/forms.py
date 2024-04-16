from typing import Any, Mapping
from django import forms
from django.core.files.base import File
from django.db.models.base import Model
from django.forms.utils import ErrorList
from .models import Account,UserProfile

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

        # if phone_number and not phone_number.isdigit():
        #   raise forms.ValidationError("Phone number must contain only digits.")
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

class UserProfileForm(forms.ModelForm):
    profile_picture = forms.ImageField(required=False, error_messages = {'invalid':("Image files only")}, widget=forms.FileInput)
    class Meta:
        model = UserProfile
        fields = ('address_line_1', 'address_line_2', 'city', 'state', 'country', 'profile_picture')

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'    