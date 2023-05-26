from django.shortcuts import render
from store.models import Product,Variation
from .models import Cart, CartItem
from django.shortcuts import redirect,get_object_or_404
from django.core.exceptions import ObjectDoesNotExist 
from django.http import HttpResponse 



# Create your views here.
def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart



def add_cart(request,product_id):
    product = Product.objects.get(id = product_id) # step 1 :  getting products
    product_variation = []
    if request.method == 'POST':
        for item in request.POST:
            key = item   #if color = black then color will b store in key and black in value
            value = request.POST[key]
            
            try:
                #iexact normalizes lower and capital letter
                variation = Variation.objects.get(product=product,variation_category__iexact=key,variation_value__iexact=value)
                product_variation.append(variation) # step 2 : from line 22 to 30 we are generating product's current variation
            except:
                pass

    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            cart_id = _cart_id(request)
        )
    cart.save() #step 3 : from line 35 to 40 we are getting the cart 

    #keeping product inside cart...so it becomes cart item(from lines 46)


    is_cart_item_exists = CartItem.objects.filter(product = product,cart=cart).exists()
    if is_cart_item_exists:
    
        #cart_item = CartItem.objects.get(product=product,cart=cart)
        cart_item = CartItem.objects.filter(product=product ,cart=cart)
        # we need existing variations->Obtained from Db
        # v need current variation-> from product_variations
        # v need item id-> from DB
        ex_var_list = []
        id = []
        for item in cart_item:
            existing_variations = item.variations.all()
            ex_var_list.append(list(existing_variations))
            id.append(item.id)

        if product_variation in ex_var_list:
            #increase product quantity
            index = ex_var_list.index(product_variation) #gives index of the variation
            item_id = id[index]
            item = CartItem.objects.get(product=product,id = item_id)
            item.quantity += 1 
            item.save()
        
        else:
            #create new cart item
            item = CartItem.objects.create(product=product,cart=cart,quantity = 1)
            if len(product_variation) > 0:
                item.variations.clear() # it clears the all the variations and after adding to cart we only get selected variation 
                                         #product variation may jave color,sizes etc
                item.variations.add(*product_variation) #I think here we r adding this product variation to our model cart_item.variation
            item.save()
      
    else:
        #if cart item does not exist ..we create new cartitem and increase its quantity by 1
       
        cart_item = CartItem.objects.create(
            product = product,
            quantity = 1,
            cart = cart
        )
        if len(product_variation)>0:
            cart_item.variations.clear()
            cart_item.variations.add(*product_variation) # here we are adding product variation to our cart_item.variation, and selected variation getting highlighted 
        cart_item.save() #step 4 : from line 43 to 53 ..we are getting cart items 
    return redirect('cart')


def remove_cart(request,product_id,cart_item_id):
    cart = Cart.objects.get(cart_id = _cart_id(request))
    product = get_object_or_404(Product, id = product_id)
    try:

        cart_item = CartItem.objects.get(cart=cart,product=product,id=cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect('cart')

def remove_cart_item(request,product_id,cart_item_id):
    cart = Cart.objects.get(cart_id = _cart_id(request))
    product = get_object_or_404(Product, id = product_id)
    cart_item = CartItem.objects.get(cart=cart,product=product,id=cart_item_id)
    cart_item.delete()
    return redirect('cart')

def cart(request,total = 0, quantity = 0,cart_items = None):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart,is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity 
        tax = (2*total)/100
        grand_total = total+tax
    except cart.DoesNotExist:
        pass 
    cart_products = []
    for cart_item in cart_items:
        cart_products.append(cart_item.product)
    context = {'total':total,'quantity':quantity,'cart_items':cart_items,'tax':tax,'grand_total':grand_total,'cart_products':cart_products}

    return render(request,'store/cart.html',context)

