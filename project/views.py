
from django.shortcuts import render
from stores.models import Product,ReviewRating
from django.shortcuts import redirect
from django.contrib import auth
from django.urls import reverse


def redirect_to_admin_login(request):
    # Redirect to the admin login page
    return redirect('/admin/login/')

def custom_admin_honeypot_logout(request):
    # Log the user out
    auth.logout(request)
    # Redirect to the admin login page
    return redirect(reverse('admin:login'))
def homepage(request):
   
    products=Product.objects.all().filter(is_available=True).order_by('created_date')
    for product in products:
        reviews  =  ReviewRating.objects.filter(product_id=product.id,status=True)

    context={

        'products': products,
        'reviews':reviews,
    }
    return render(request,"home.html",context)

