from django.shortcuts import render,redirect,get_object_or_404
from .models import Product,ReviewRating,ProductGallery
from category.models import Category
from django.db.models import Q
from carts.views import _cart_id
from django.core.paginator import EmptyPage,PageNotAnInteger,Paginator
from django.http import HttpResponse
from carts.models import CartItem
from django.contrib import messages
from .forms import ReviewForm
from orders.models import OrderProduct
# Create your views here.
def store(request,category_slug=None):
    categories =None
    products =None

    if category_slug!= None:
        categories= get_object_or_404(Category,slug=category_slug)
        products= Product.objects.filter(category=categories,is_available=True)
        paginator =Paginator(products,6)
        page=request.GET.get('page')
        paged_products=paginator.get_page(page)
        product_count = products.count()
    else:        
      products=Product.objects.all().filter(is_available=True).order_by('id')
      paginator =Paginator(products,10)
      page=request.GET.get('page')
      paged_products=paginator.get_page(page)
      product_count = products.count()


    context={

        'products': paged_products,
        'product_count': product_count
    }

    return render(request,'stores/store.html',context)

def product_details(request,category_slug,product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug,slug=product_slug)
        in_cart=CartItem.objects.filter(cart__cart_id=_cart_id(request),product=single_product).exists()
        
    except Exception as e:
      raise e
    
    if request.user.is_authenticated:
      try:
         orderproduct = OrderProduct.objects.filter(user=request.user,product_id=single_product.id).exists()
      except OrderProduct.DoesNotExist:
        orderproduct =None
    else:
         orderproduct =None
    reviews  =  ReviewRating.objects.filter(product_id=single_product.id,status=True)
       
    product_gallery =ProductGallery.objects.filter(product_id=single_product.id)
    context ={
        'single_product' : single_product,
         'in_cart':in_cart,
         'orderproduct': orderproduct,
         'reviews': reviews,
         'product_gallery': product_gallery
    }
    return render(request,'stores/product_details.html',context)
   


def search(request):
    keyword = request.GET.get('keyword', '').strip()
    
    if not keyword:  # If search bar is empty
        return render(request, 'stores/store.html', {'products': [], 'product_count': 0})
    
    products = Product.objects.order_by('-created_date').filter(
        Q(description__icontains=keyword) | Q(product_name__icontains=keyword)
    )
    product_count = products.count()
    
    context = {
        'products': products,
        'product_count': product_count,
    }
    
    return render(request, 'stores/store.html', context)
# def search(request):
#     products = []  # Initialize products as an empty list
#     product_count = 0  # Initialize product_count as 0
#     if 'keyword' in request.GET:
#          keyword = request.GET['keyword']
#          if keyword:
#            products = Product.objects.order_by('-created_date').filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword))
#            product_count = products.count()
#          context ={
#             'products': products,
#              'product_count':product_count,
#            }
#     return render(request,'stores/store.html',context)

# def filter_products(request):
#     category_slug = request.GET.get('category')
#     sizes = request.GET.getlist('size')
#     min_price = request.GET.get('min_price')
#     max_price = request.GET.get('max_price')

#     # Filter products based on selected category
#     products = Product.objects.filter(is_available=True)
#     if category_slug:
#         products = products.filter(category__slug=category_slug)

#     # Filter products based on selected sizes
#     if sizes:
#         products = products.filter(size__in=sizes)

#     # Filter products based on selected price range
#     if min_price and max_price:
#         products = products.filter(price__range=(min_price, max_price))

#     product_count = products.count()

#     context = {
#         'products': products,
#         'product_count': product_count,
#     }

    # return render(request, 'stores/store.html', context)
def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            reviews = ReviewRating.objects.get(user__id=request.user.id, product__id=product_id)
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            messages.success(request, 'Thank you! Your review has been updated.')
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(request, 'Thank you! Your review has been submitted.')
                return redirect(url)
            


def about_us(request):
    return render(request, 'stores/about_us.html')

def privacy_policy(request):
    return render(request, 'stores/privacy.html')

def terms_conditions(request):
    return render(request, 'stores/terms_conditions.html')
