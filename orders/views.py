from django.shortcuts import render, redirect
from django.http import  HttpResponse,JsonResponse

from carts.models import CartItem
from .forms import OrderForm
import datetime
from .models import Order,Payment,OrderProduct
import json
from stores.models import Product
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
import razorpay
from django.conf import settings
from decouple import config

client = razorpay.Client(auth=(config('RAZOR_PAY_KEY_ID'), config('RAZOR_PAY_KEY_SECRET')))


def payments(request):
    # if request.method == 'POST':
        
            body = json.loads(request.body)
            try:
                  order = Order.objects.get(user=request.user, is_ordered=False, order_number=body['orderID'])
            except Order.DoesNotExist:
             # Handle the case where the order doesn't exist
                     return HttpResponse("Order not found")
            # order = Order.objects.get(user=request.user, is_ordered=False, order_number=body['orderID'])
           

            payment = Payment(
                user=request.user,
                payment_id=body['transID'],
                payment_method=body['payment_method'],
                amount_paid=order.order_total,
                status=body['status'],
            )
            payment.save()

            order.payment = payment
            order.is_ordered = True
            order.save()

            # move the cart items to order product table
            cart_items = CartItem.objects.filter(user=request.user)

            for item in cart_items:
                 orderproduct = OrderProduct()
                 orderproduct.order_id = order.id
                 orderproduct.payment = payment
                 orderproduct.user_id = request.user.id
                 orderproduct.product_id = item.product_id
                 orderproduct.quantity = item.quantity
                 orderproduct.product_price = item.product.price
                 orderproduct.ordered = True
                 orderproduct.save()

                 cart_item = CartItem.objects.get(id=item.id)
                 product_variation = cart_item.variations.all()
                 orderproduct = OrderProduct.objects.get(id=orderproduct.id)
                 orderproduct.variations.set(product_variation)
                 orderproduct.save()

                 # reduce the quantity of the sold products
                 product = Product.objects.get(id=item.product_id)
                 product.stock -= item.quantity
                 product.save()


           # clear the cart
            CartItem.objects.filter(user=request.user).delete()


            # send the order recieved  mail to the customer
            mail_subject = 'Thank you for your order!'
            message = render_to_string('orders/order_recieved_email.html', {
                'user': request.user,
                'order': order,
            })
            to_email = request.user.email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            # send order number and transaction id back to senddata method via jsonResponse
            data = {
            'order_number': order.order_number,
            'transID': payment.payment_id,
            }
            return JsonResponse(data)

            

            

           
           
 
def place_order(request, total=0, quantity=0):
    current_user = request.user

    # If the cart count is less than or equal to 0, then redirect back to shop
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()            
    if cart_count <= 0:
        return redirect('store')

    grand_total = 0
    tax = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (2 * total)/100
    grand_total = total + tax

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Store all the billing information inside Order table
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()
            # Generate order number
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr, mt, dt)
            current_date = d.strftime("%Y%m%d") #20210305
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
            razorpay_order = client.order.create(data={
                'amount': int(grand_total * 100),  # Amount in paise
                'currency': 'INR',
                'payment_capture': 1  # Auto capture payment
            })
            print("Razorpay Order:", razorpay_order)  # Add this line to print Razorpay order

            # Print Razorpay key ID to verify it's correct
            razorpay_key_id = settings.RAZOR_PAY_KEY_ID
            print("Razorpay Key ID:", razorpay_key_id)

            context = {
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'tax': tax,
                'grand_total': grand_total,
                'razorpay_order': razorpay_order,
                'razorpay_key_id': razorpay_key_id,
            }
            return render(request, 'orders/payments.html', context)
            
           
           
    else:
     return redirect('checkout')
            # # Add print statement to debug form errors
            # print("Form is not valid:", form.errors)
        
    # else:
    #     # Add print statement to verify that request method is not POST
    #     print("Request method is not POST")

    # # Redirect to checkout if the request method is not POST
    # return redirect('checkout')

def order_complete(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')

    try: 

            
         order = Order.objects.get(order_number=order_number, is_ordered=True)
         ordered_products = OrderProduct.objects.filter(order_id=order.id)

         subtotal = 0
         for i in ordered_products:
            subtotal += i.product_price * i.quantity

         payment = Payment.objects.get(payment_id=transID)

         context = {
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order.order_number,
            'transID': payment.payment_id,
            'payment': payment,
            'subtotal': subtotal,
         }
         return render(request, 'orders/order_complete.html',context)
    except (Payment.DoesNotExist, Order.DoesNotExist):
         return redirect('home')    

def my_view(request):
    razorpay_key = settings.RAZOR_PAY_KEY_ID
    context = {
        'razorpay_key': razorpay_key,
        # other context variables
    }
    return render(request, 'payments.html', context)    

    
    
    
