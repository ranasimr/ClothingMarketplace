ducts,
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