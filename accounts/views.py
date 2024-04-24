from django.shortcuts import render,redirect,get_object_or_404
from .forms import RegistrationForm ,UserForm,UserProfileForm
from .models import  Account,UserProfile
from orders.models import Order,OrderProduct
from django.contrib import messages, auth    
from django.contrib.auth.decorators import  login_required  
from django.utils.decorators import method_decorator 
from django.urls import reverse 
from django.http import HttpResponseRedirect 
from stores.models import Product
from django.http import HttpResponse, JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import update_session_auth_hash
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.contrib import messages

from carts.views import _cart_id
from carts.models import Cart,CartItem
import requests

from .forms import AddressForm
from .models import Address
from django.views.generic import View

from django.contrib.auth.models import User, Group
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission




def homepage(request):

     products=Product.objects.all().filter(is_available=True)

     context={

        'products': products,
    }
    
    # Add any logic here for the home page
     return render(request, 'home.html',context)

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username=email.split("@")[0]
            user = Account.objects.create_user(first_name=first_name,last_name=last_name,email=email, username=username ,password=password)
            user.phone_number= phone_number
            user.save()

            #user activation 
            current_site = get_current_site(request)
            mail_subject = "Please activate you account."
            message = render_to_string('accounts/account_verification_email.html',{
                'user' : user,
                'domain': current_site,
                'uid' : urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),


            })
            to_email = email
            send_email = EmailMessage( mail_subject, message, to=[to_email])
            send_email.send()
            # messages.success(request,'Thank you for registering with us.We have sent you a verification email address.Please verify it .')
            return redirect('/accounts/login/?command=verification&email='+email)
    else:
       form = RegistrationForm()
    
    context ={
        'form':form,
    }
    return render (request, 'accounts/register.html',context)

def login(request):
    if request.method =='POST':
        email = request.POST['email']
        password = request.POST['password']
        user = auth.authenticate(email=email, password=password)

        if user is not None:
            try:
                cart= Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exists =CartItem.objects.filter(cart=cart).exists()
                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart)
                    
                    #getting the product variation by cart_id
                    product_variation=[]
                    for item in cart_item:
                         variation = item.variations.all()
                         product_variation.append(list(variation))
                         
                    # getting the cart item from the user to access his products variations
                    cart_item = CartItem.objects.filter(user=user)
                    
                    ex_var_list=[]
                    id = []
                    for item in cart_item:
                        existing_variation = item.variations.all()
                        ex_var_list.append(list(existing_variation))
                        id.append(item.id)    

                    for pr in product_variation:
                        if pr in ex_var_list:
                            index= ex_var_list.index(pr)
                            item_id= id[index]
                            item =CartItem.objects.get(id=item_id)
                            item.quantity += 1
                            item.user =user
                            item.save()
                        else:
                            cart_item =CartItem.objects.filter(cart=cart)
                            for item in cart_item:
                                item.user =user
                                item.save()



                          

                 
            except:
                  print
                  pass
            
            auth.login(request,user)
            messages.success(request,"You are now logged in")
            url =request.META.get('HTTP_REFERER')


            # Check if the user has a profile
            try:
                user_profile = UserProfile.objects.get(user=user)
                if not user_profile.address_line_1:
                    messages.info(request, "Please complete your profile by adding an address.")
            except UserProfile.DoesNotExist:
                messages.info(request, "Please complete your profile by adding an address.")
            
            try:
                query= requests.utils.urlparse(url).query
               
                params=dict(x.split('=') for x in query.split('&'))
                if'next' in params:
                    nextPage= params['next']
                    return redirect(nextPage)
            
                
            except:
                return redirect('dashboard')
                # return redirect('home')
        else:
            messages.error(request,'Invalid login credentials')
            return redirect('login')
        
    return render (request, 'accounts/login.html')


@login_required(login_url='login')
def logout(request):
     auth.logout(request)
     messages.success(request,'You are Logged Out')
     return HttpResponseRedirect(reverse('login'))






def activate(request,uidb64,token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user,token):
        user.is_active = True
        user.save()
        messages.success(request,'Congratulations! Your account is activated.')
        return redirect('login')
    else:
        messages.error(request,'Invalid activation link')
        return redirect('register')
@login_required(login_url='login')
def dashboard(request):
    orders = Order.objects.order_by('-created_at').filter(user_id=request.user.id, is_ordered=True)
    orders_count = orders.count()

    # Retrieve or create the user's profile
    userprofile, created = UserProfile.objects.get_or_create(user=request.user)

    context = {
        'orders_count': orders_count,
        'userprofile': userprofile,
    }
    return render(request, 'accounts/dashboard.html', context) 


def forgotPassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists(): 
            user = Account.objects.get(email__exact=email)
            #reset 
            current_site = get_current_site(request)
            mail_subject = "Please reset Your password."
            message = render_to_string('accounts/reset_password_email.html',{
                'user' : user,
                'domain': current_site,
                'uid' : urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            messages.success(request,'Password reset email has been sent to your email address')
            return redirect('login')
        else:
            messages.error(request,'Account does not exist!')
            return redirect('forgotPassword')
    else:
        return render(request,'accounts/forgotPassword.html')
 
def resetpassword_validate(request,uidb64,token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user,token):
        request.session['uid']=uid
        messages.success(request,'Please reset your password ')
        return redirect('resetPassword')
    else:
        messages.error(request,'This link has been expired!')
        return redirect('login')
    
def resetPassword(request):
    if request.method =='POST':
        password =request.POST['password']
        confirm_password =request.POST['confirm_password']

        if password ==confirm_password:
            uid=request.session.get('uid')
            user=Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request,'Password reset Successfully')
            return redirect('login')
        else:
            messages.error(request,'password do not match!')
            return redirect('resetPassword')
           
    else:
        return render(request,'accounts/resetPassword.html')
    
@login_required(login_url='login')
def my_orders(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')
    context = {
        'orders': orders,
    }
    return render(request, 'accounts/my_orders.html', context) 

@login_required(login_url='login')
def edit_profile(request):
    userprofile = get_object_or_404(UserProfile, user=request.user)
    print(userprofile.profile_picture)
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=userprofile)
       
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('edit_profile')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=userprofile)
    
    # Check if profile picture exists
    profile_picture_url = None
    if userprofile.profile_picture:
        profile_picture_url = userprofile.profile_picture.url

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'userprofile': userprofile,
        'profile_picture_url': profile_picture_url,  # Pass profile picture URL to the template
    }
    return render(request, 'accounts/edit_profile.html', context)


# @login_required(login_url='login')
# def edit_profile(request):
#     userprofile = get_object_or_404(UserProfile, user=request.user)
#     print(userprofile.profile_picture)
#     if request.method == 'POST':
#         user_form = UserForm(request.POST, instance=request.user)
#         profile_form = UserProfileForm(request.POST, request.FILES, instance=userprofile)
#         if user_form.is_valid() and profile_form.is_valid():
#             user_form.save()
#             profile_form.save()

#             # Save additional address fields if present
#             for i in range(3):  # Assuming you allow up to 3 additional addresses
#                 address_field_name = f'address_line_{i + 3}'  # Start from 3 as first additional address
#                 if address_field_name in request.POST:
#                     setattr(userprofile, address_field_name, request.POST[address_field_name])
#             userprofile.save()

#             messages.success(request, 'Your profile has been updated.')
#             return redirect('edit_profile')
#     else:
#         user_form = UserForm(instance=request.user)
#         profile_form = UserProfileForm(instance=userprofile)
    
#     profile_picture_url = None
#     if userprofile.profile_picture:
#         profile_picture_url = userprofile.profile_picture.url

    
#     context = {
#         'user_form': user_form,
#         'profile_form': profile_form,
#         'userprofile': userprofile,
#         'profile_picture_url': profile_picture_url,
#     }
#     return render(request, 'accounts/edit_profile.html', context)

# @login_required(login_url='login')
# def edit_profile(request):

#     userprofile = get_object_or_404(UserProfile, user=request.user)
#     print(userprofile.profile_picture)
    
#     if request.method == 'POST':
#         user_form = UserForm(request.POST, instance=request.user)
#         profile_form = UserProfileForm(request.POST, request.FILES, instance=userprofile)

#         if 'action' in request.POST and request.POST['action'] == 'add_address':
#             # Add logic to handle adding additional address fields here
#             pass
#         else:
#             # Process user profile form if the form is valid
#             if user_form.is_valid() and profile_form.is_valid():
#                 user_form.save()
#                 profile_form.save()
                
#                 # Save additional address fields if present
#                 for i in range(5):
#                     address_field_name = f'address_line_{i + 1}'
#                     if address_field_name in request.POST:
#                         setattr(userprofile, address_field_name, request.POST[address_field_name])
#                 userprofile.save()

#                 messages.success(request, 'Your profile has been updated.')
#                 return redirect('edit_profile')

#     else:
#         user_form = UserForm(instance=request.user)
#         profile_form = UserProfileForm(instance=userprofile)
    
#     profile_picture_url = None
#     if userprofile.profile_picture:
#         profile_picture_url = userprofile.profile_picture.url

#     additional_address_fields = []  # Initialize additional address fields
    
#     context = {
#         'user_form': user_form,
#         'profile_form': profile_form,
#         'userprofile': userprofile,
#         'profile_picture_url': profile_picture_url,
#         'additional_address_fields': additional_address_fields,
#     }
#     return render(request, 'accounts/edit_profile.html', context)


@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        user = request.user

        # Check if the new password meets complexity requirements
        if not is_valid_password(new_password):
            messages.error(request, 'Password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, one number, and one special character.')
            return redirect('change_password')

        if new_password == confirm_password:
            # Check if the current password is correct
            if user.check_password(current_password):
                user.set_password(new_password)
                user.save()
                # Update the user's session authentication hash to prevent them from being logged out
                update_session_auth_hash(request, user)
                messages.success(request, 'Password updated successfully.')
                return redirect('change_password')
            else:
                messages.error(request, 'Please enter the correct current password.')
                return redirect('change_password')
        else:
            messages.error(request, 'Passwords do not match.')
            return redirect('change_password')
    return render(request, 'accounts/change_password.html')

def is_valid_password(password):
    # Password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, one number, and one special character
    if len(password) < 8:
        return False
    has_uppercase = any(char.isupper() for char in password)
    has_lowercase = any(char.islower() for char in password)
    has_digit = any(char.isdigit() for char in password)
    has_special = any(char in '@#$%^&!*?|' for char in password)
    return has_uppercase and has_lowercase and has_digit and has_special
# def change_password(request):
#     if request.method == 'POST':
#         current_password = request.POST['current_password']
#         new_password = request.POST['new_password']
#         confirm_password = request.POST['confirm_password']

#         user = Account.objects.get(username__exact=request.user.username)

#         if new_password == confirm_password:
#             success = user.check_password(current_password)
#             if success:
#                 user.set_password(new_password)
#                 user.save()
#                 # auth.logout(request) by default logout in django
#                 messages.success(request, 'Password updated successfully.')
#                 return redirect('change_password')
#             else:
#                 messages.error(request, 'Please enter valid current password')
#                 return redirect('change_password')
#         else:
#             messages.error(request, 'Password does not match!')
#             return redirect('change_password')
#     return render(request, 'accounts/change_password.html')





@login_required(login_url='login')
def order_detail(request, order_id):
    order = get_object_or_404(Order, order_number=order_id)
    order_detail = order.orderproduct_set.all()
    subtotal = sum(item.product_price * item.quantity for item in order_detail)

    # Check if the current user has purchased each product in the order
    has_purchased_products = all(OrderProduct.objects.filter(product=item.product, order=order, order__user=request.user).exists() for item in order_detail)

    context = {
        'order_detail': order_detail,
        'order': order,
        'subtotal': subtotal,
        'has_purchased_products': has_purchased_products,  # Pass the information to the template
    }
    return render(request, 'accounts/order_detail.html', context)

# @login_required(login_url='login')
# def order_detail(request, order_id):
#     order_detail = OrderProduct.objects.filter(order__order_number=order_id)
#     order = Order.objects.get(order_number=order_id)
#     subtotal = 0
#     for i in order_detail:
#         subtotal += i.product_price * i.quantity

#     context = {
#         'order_detail': order_detail,
#         'order': order,
#         'subtotal': subtotal,
#     }
#     return render(request, 'accounts/order_detail.html', context)




# @login_required(login_url='login')
# def add_address(request):
#     if request.method == 'POST':
#         form = AddressForm(request.POST)
#         if form.is_valid():
#             # Save the address to the database
#             address = form.save(commit=False)
#             address.user = request.user  # Assuming you have user authentication enabled
#             address.save()
#             # Optionally, you can add a success message
#             messages.success(request, 'Address added successfully.')
#             # Redirect the user to a different page or reload the same page
#             return redirect('add_address')  # Redirect to the same page to clear the form
        
#         #  # Check if the delete parameter is present in the POST request
#         # elif 'delete_address_id' in request.POST:
#         #     address_id = request.POST.get('delete_address_id')
#         #     address = get_object_or_404(Address, pk=address_id, user=request.user)
#         #     address.delete()
#         #     # Optionally, you can add a success message for deletion
#         #     messages.success(request, 'Address deleted successfully.')
#         #     return redirect('add_address')  # Redirect to the same page after deletion

#     else:
#         form = AddressForm()
    
#     # Retrieve and pass saved addresses to the template context
#     saved_addresses = Address.objects.filter(user=request.user)  # Assuming you have a ForeignKey relationship to the user model

#     # if request.method == 'POST' and 'delete_address_id' in request.POST:
#     #     address_id = request.POST.get('delete_address_id')
#     #     address = get_object_or_404(Address, pk=address_id, user=request.user)
#     #     address.delete()
#     #     # Optionally, you can add a success message for deletion
#     #     messages.success(request, 'Address deleted successfully.')
#     #     return redirect('add_address')  # Redirect to the same page after deletion
    

#     return render(request, 'accounts/add_address.html', {'form': form, 'saved_addresses': saved_addresses})


# @login_required(login_url='login')
# def delete_address(request, address_id):
#     address = get_object_or_404(Address, pk=address_id)
#     if address.user == request.user:
#         address.delete()
#         return JsonResponse({'message': 'Address deleted successfully.'})
#     else:
#         return JsonResponse({'error': 'You are not authorized to delete this address.'}, status=403)

# @login_required(login_url='login')
# def add_address(request):
#     if request.method == 'POST':
#         address_form = AddressForm(request.POST)
#         if address_form.is_valid():
#             address = address_form.save(commit=False)
#             address.user = request.user  # Assuming you have authentication enabled
#             address.save()
#             return redirect('dashboard')  # Redirect to dashboard or any other page after adding the address
#     else:
#         address_form = AddressForm()
#     return render(request, 'accounts/add_address.html', {'address_form': address_form})




# class AddAddressView(View):
#     def get(self, request):
#         form = AddressForm()
#         saved_addresses = Address.objects.filter(user=request.user)

#         # Check if the user has a profile and if the profile address is available
#         try:
#             user_profile = UserProfile.objects.get(user=request.user)
#             profile_address = {
#                 'address_line_1': user_profile.address_line_1,
#                 'address_line_2': user_profile.address_line_2,
#                 'city': user_profile.city,
#                 'state': user_profile.state,
#                 'country': user_profile.country
#             }
#             if all(profile_address.values()):
#                 # Prepopulate the AddressForm with the profile address
#                 form = AddressForm(initial=profile_address)
#         except UserProfile.DoesNotExist:
#             pass

#         return render(request, 'accounts/add_address.html', {'form': form, 'saved_addresses': saved_addresses})

#     def post(self, request):
#         form = AddressForm(request.POST)
#         if form.is_valid():
#             address = form.save(commit=False)
#             address.user = request.user
#             address.save()
#             messages.success(request, 'Address added successfully.')
#             return redirect('add_address')
#         else:
#             saved_addresses = Address.objects.filter(user=request.user)
#             return render(request, 'accounts/add_address.html', {'form': form, 'saved_addresses': saved_addresses})







class AddAddressView(View):
    def get(self, request):
        form = AddressForm()
        saved_addresses = Address.objects.filter(user=request.user)
        return render(request, 'accounts/add_address.html', {'form': form, 'saved_addresses': saved_addresses})
    
    def post(self, request):
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request, 'Address added successfully.')
            return redirect('add_address')
        else:
            saved_addresses = Address.objects.filter(user=request.user)
            return render(request, 'accounts/add_address.html', {'form': form, 'saved_addresses': saved_addresses})
        



@login_required(login_url='login')
def delete_address(request, address_id):
    # Get the address object
    address = get_object_or_404(Address, pk=address_id)

    # Check if the user is authorized to delete the address
    if address.user == request.user:
        # Delete the address
        address.delete()
        messages.success(request, 'Address deleted successfully.')
    else:
         # Display error message if the user is not authorized
        messages.error(request, 'You are not authorized to delete this address.')

    return redirect('add_address')
