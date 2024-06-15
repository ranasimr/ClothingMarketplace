from django.shortcuts import render, redirect, get_object_or_404
from stores.models import Product, Variation
from django.contrib import messages
from .models import Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from accounts.models import Address

# Generate or retrieve cart ID from session
def _cart_id(request):
    cart_id = request.session.get('cart_id')
    if not cart_id:
        cart_id = request.session.session_key
        request.session['cart_id'] = cart_id
        request.session.save()  # Save the session explicitly
    return cart_id

# Add a product to the cart
def add_cart(request, product_id):
    current_user = request.user
    product = Product.objects.get(id=product_id)
    
    if current_user.is_authenticated:
        product_variation = []
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]
                try:
                    variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                    product_variation.append(variation)
                except Variation.DoesNotExist:
                    pass
    
            # Check if a similar cart item exists based on product and variations
            similar_cart_items = CartItem.objects.filter(product=product, user=current_user, variations__in=product_variation)
            
            if similar_cart_items.exists():
                # If similar cart items exist, check if all variations are the same
                for cart_item in similar_cart_items:
                    if set(cart_item.variations.all()) == set(product_variation):
                        # If all variations are the same, increment the quantity
                        cart_item.quantity += 1
                        cart_item.save()
                        return redirect('cart')
            
            # If all variations are not the same or no similar cart items exist, create a new cart item
            cart_item = CartItem.objects.create(product=product, quantity=1, user=current_user)
            cart_item.variations.add(*product_variation)
            cart_item.save()
        return redirect('cart')
    else:
        product_variation = []
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]
                try:
                    variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                    product_variation.append(variation)
                except Variation.DoesNotExist:
                    pass
    
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
            except Cart.DoesNotExist:
                cart = Cart.objects.create(cart_id=_cart_id(request))
                cart.save()
            
            similar_cart_items = CartItem.objects.filter(product=product, cart=cart, variations__in=product_variation)
            
            if similar_cart_items.exists():
                for cart_item in similar_cart_items:
                    if set(cart_item.variations.all()) == set(product_variation):
                        cart_item.quantity += 1
                        cart_item.save()
                        return redirect('cart')
            
            cart_item = CartItem.objects.create(product=product, quantity=1, cart=cart)
            cart_item.variations.add(*product_variation)
            cart_item.save()
        
        return redirect('cart')

def remove_cart(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect('cart')

def remove_cart_item(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
    cart_item.delete()
    return redirect('cart')

def cart(request, total=0, quantity=0, cart_items=None):
    try:
        tax = 0
        grand_total = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2 * total) / 100
        grand_total = total + tax
    except ObjectDoesNotExist:
        pass 

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
    }
    
    return render(request, 'stores/cart.html', context)

@login_required(login_url='login')
def checkout(request, total=0, quantity=0, cart_items=None):
    try:
        tax = 0
        grand_total = 0
        saved_addresses = None  # Initialize saved_addresses here
        
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        
        tax = (2 * total) / 100
        grand_total = total + tax
        
        # Retrieve saved addresses for the logged-in user
        if request.user.is_authenticated:
            saved_addresses = Address.objects.filter(user=request.user)

       

        # Handle address selection
        if request.method == 'POST' and 'choose_address_btn' in request.POST:
            selected_address_id = request.POST.get('selected_address')
            if selected_address_id:
                try:
                    selected_address = Address.objects.get(id=selected_address_id)
                    # Populate address fields with the selected address
                    request.session['selected_address'] = {
                        'address_line_1': selected_address.address_line_1,
                        'address_line_2': selected_address.address_line_2,
                        'city': selected_address.city,
                        'state': selected_address.state,
                        'country': selected_address.country,
                    }
                except Address.DoesNotExist:
                    pass

        

        # Define the context dictionary
        context = {
            'total': total,
            'quantity': quantity,
            'cart_items': cart_items,
            'tax': tax,
            'grand_total': grand_total,
            'saved_addresses': saved_addresses,
            
        }

    except ObjectDoesNotExist:
        pass

    return render(request, 'stores/checkout.html', context)

# @login_required(login_url='login')
# def checkout(request, total=0, quantity=0, cart_items=None):
#     try:
#         tax = 0
#         grand_total = 0
#         if request.user.is_authenticated:
#             cart_items = CartItem.objects.filter(user=request.user, is_active=True)
#         else:
#             cart = Cart.objects.get(cart_id=_cart_id(request))
#             cart_items = CartItem.objects.filter(cart=cart, is_active=True)
#         for cart_item in cart_items:
#             total += (cart_item.product.price * cart_item.quantity)
#             quantity += cart_item.quantity
#         tax = (2 * total) / 100
#         grand_total = total + tax

#         # Retrieve saved addresses for the logged-in user
#         saved_addresses = None
#         if request.user.is_authenticated:
#             saved_addresses = Address.objects.filter(user=request.user)

#     except ObjectDoesNotExist:
#         pass 

#     context = {
#         'total': total,
#         'quantity': quantity,
#         'cart_items': cart_items,
#         'tax': tax,
#         'grand_total': grand_total,
#         'saved_addresses': saved_addresses,
#     }  

#     # Handle address selection
#     if request.method == 'POST' and 'choose_address_btn' in request.POST:
#         selected_address_id = request.POST.get('selected_address')
#         if selected_address_id:
#             try:
#                 selected_address = Address.objects.get(id=selected_address_id)
#                 # Populate address fields with the selected address
#                 request.session['selected_address'] = {
#                     'address_line_1': selected_address.address_line_1,
#                     'address_line_2': selected_address.address_line_2,
#                     'city': selected_address.city,
#                     'state': selected_address.state,
#                     'country': selected_address.country,
#                 }
#             except Address.DoesNotExist:
#                 pass

#     return render(request, 'stores/checkout.html', context)

# @login_required(login_url='login')
# def checkout(request):
#     total = 0
#     quantity = 0
#     tax = 0
#     grand_total = 0
#     cart_items = None
#     saved_addresses = None
#     first_name = ''
#     last_name = ''
#     email = ''
#     phone = ''

#     try:
#         if request.user.is_authenticated:
#             # Fetch cart items
#             cart_items = CartItem.objects.filter(user=request.user, is_active=True)
#             for cart_item in cart_items:
#                 total += (cart_item.product.price * cart_item.quantity)
#                 quantity += cart_item.quantity

#             tax = (2 * total) / 100
#             grand_total = total + tax

#             # Fetch saved addresses
#             saved_addresses = Address.objects.filter(user=request.user)

#             # Get user account information
#             user = request.user
#             first_name = user.first_name
#             last_name = user.last_name
#             email = user.email
#             phone = user.phone_number  # Assuming you have a phone_number field in your Account model
            
#     except CartItem.DoesNotExist:
#         pass
#     except Address.DoesNotExist:
#         pass

#     context = {
#         'total': total,
#         'quantity': quantity,
#         'cart_items': cart_items,
#         'tax': tax,
#         'grand_total': grand_total,
#         'saved_addresses': saved_addresses,
#         'first_name': first_name,
#         'last_name': last_name,
#         'email': email,
#         'phone': phone,
#     }

#     return render(request, 'stores/checkout.html', context)