
from django.shortcuts import render, redirect,get_object_or_404
from stores.models import Product,Variation
from .models import Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse


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
    if request.method == 'POST':
     for item in request.POST:
         key =item
         value= request.POST[key]
         try:
             variation= Variation.objects.get(variation_category_iexact=key,variation_value__iexact=value)
             print(variation)
         except:
             pass    

    product = Product.objects.get(id=product_id)

    
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id=_cart_id(request))

    try:
        cart_item = CartItem.objects.get(product=product, cart=cart)
        cart_item.quantity += 1
        cart_item.save()
    except CartItem.DoesNotExist:
        cart_item = CartItem.objects.create(
            product=product,
            quantity=1,
            cart=cart,
        )
    return redirect('cart')


def remove_cart(request,product_id):
    cart =Cart.objects.get(cart_id=_cart_id(request))
    product =get_object_or_404(Product, id=product_id)
    cart_item =CartItem.objects.get(product=product, cart=cart)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart')    


def remove_cart_item(request, product_id):
    cart =Cart.objects.get(cart_id=_cart_id(request))
    product =get_object_or_404(Product, id=product_id)
    cart_item= CartItem.objects.get(product=product,cart=cart)
    cart_item.delete()
    return redirect('cart')


   

# View to display the cart
def cart(request,total=0,quantity=0,cart_items=None):
    try:
        cart= Cart.objects.get(cart_id=_cart_id(request))
        cart_items= CartItem.objects.filter(cart=cart,is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax =(2* total)/100
        grand_total = total+ tax
    except ObjectDoesNotExist:
        pass 

    context ={
        'total': total,
        'quantity':quantity,
        'cart_items':cart_items,
        'tax':tax,
        'grand_total':grand_total,

    }        

    return render(request, 'stores/cart.html',context)