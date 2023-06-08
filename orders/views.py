from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from cart.models import Cart,CartItem
from store.models import Product
from django.shortcuts import redirect
from .forms import OrderForm
from .models import Order,Payment,OrderProduct
import datetime
import json
from django.template.loader import render_to_string
from django.core.mail import EmailMessage


# Create your views here.
def payments(request):

    body = json.loads(request.body) #it gives all the transactional details
    order = Order.objects.get(user=request.user,is_ordered=False,order_number=body['orderID'] )
    print('**********')
    print(body)
        
    #store transaction details inside payment model
    payment = Payment(
        user = request.user,
        payment_id = body['transID'],
        payment_method = body['payment_method'],
        amount_paid = order.order_total,
        status = body['status'], 
    )
    payment.save()
    #after saving the payment...we have to also store it in our Order model
    order.payment = payment
    order.is_ordered = True #after the payment is done we have to set is_ordered = True
    
    order.save()

    #Move the cart items to Order Product table
    cart_items  = CartItem.objects.filter(user=request.user)

    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id #we have order on line 14
        orderproduct.payment = payment
        orderproduct.user_id = request.user.id
        orderproduct.product_id = item.product_id
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.product.price 
        orderproduct.ordered = True #as payment is successfull it is TRUE
        orderproduct.save()
        #after saving the order product...it generates id for it

        cart_item = CartItem.objects.get(id=item.id)
        variations = cart_item.variations.all()
        orderproduct = OrderProduct.objects.get(id=orderproduct.id)
        orderproduct.variations.set(variations)
        orderproduct.save()

        # Reduce the quantity of the sold products
        product = Product.objects.get(id=item.product_id)
        product.stock -= item.quantity 
        product.save()

    # clear the cart
    CartItem.objects.filter(user = request.user).delete()



    #send order received email to customer
    mail_subject = 'Thank you for your order'
    message = render_to_string('orders/order_received_email.html',{
        'user':request.user,
        'order':order,

    })
    to_email = order.email
    send_email = EmailMessage(mail_subject,message,to=[to_email])
    send_email.send()

    #send order number and transaction id back to send data method via Json response
    data = {
        'order_number': order.order_number,
        'transID' : payment.payment_id,

    }
    return JsonResponse(data)


    #return render(request,'orders/payments.html' )


def place_order(request,total=0):
    current_user = request.user

    #if the cart count <= 0 ..then redirect back to shop 
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('store')
    
    grand_total = 0
    tax = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
    tax = (2*total)/100
    grand_total = total+tax
    
    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            #store all the billing info inside order table
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
            #to get user ip 
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()
            #generate order number by using currentdate and order_id(which comes after data.save)
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr,mt,dt)
            current_date = d.strftime("%Y%m%d") #20230603
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            #retreiving from order model after saving the data through post request
            order = Order.objects.get(user = current_user,is_ordered = False, order_number = order_number)
            context = {
                'order': order,
                'cart_items': cart_items,
                'grand_total': grand_total,
                'tax': tax,
                'total':total
            }

            return render(request,'orders/payments.html',context)
        else:
            print(form.errors)
    else:
        return redirect('checkout')

def order_complete(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')

    try:
        order = Order.objects.get(order_number=order_number,is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)
        sub_total = 0
        
        for i in ordered_products:
            sub_total += i.product_price * i.quantity
            
        
        payment = Payment.objects.get(payment_id=transID)
        for item in ordered_products:
            print(item.variations)

        context = {
            'order':order,
            'ordered_products':ordered_products,
            'transID':transID,
            'subtotal':sub_total,
            'payment': payment
            
        }
        return render(request,'orders/order_complete.html',context)
    except (Payment.DoesNotExist,Order.DoesNotExist):
        return HttpResponse('Error')
    
