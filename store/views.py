from django.shortcuts import render, get_object_or_404
from .models import Product
from category.models import Category
from cart.models import Cart,CartItem
from cart.views import _cart_id
from django.http import HttpResponse
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse
from django.db.models import Q

# Create your views here.
def store(request,category_slug=None):
    
    categories = None 
    products = None 

    if category_slug != None:
        categories = get_object_or_404(Category,slug = category_slug)
        products = Product.objects.filter(category=categories, is_available = True).order_by('id')
        paginator = Paginator(products, 1)
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        count = len(products)
    else:
        products = Product.objects.all().filter(is_available = True).order_by('id')
        paginator = Paginator(products, 3 )
        page = request.GET.get('page')
        paged_products = paginator.get_page(page)
        count = len(products)
    


    context = {
        'products' :  paged_products,
        'count' : count
    }

    return render(request,'store/store.html', context)

def product_detail(request,category_slug, product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug,slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request),product=single_product).exists()
      
    except Exception as e:
        raise e
    context = {'single_product':single_product,'in_cart':in_cart}
    return render(request,'store/product_detail.html', context )

def search(request):
    #we have used get method
    if 'keyword' in request.GET: #checking if get req has keyword or not
        keyword = request.GET['keyword'] #if the value is present we are storing it in the keyword variable
        if keyword: #if keyword is not blank
            products = Product.objects.order_by('-created_date').filter(Q(description__icontains=keyword) | Q(product_name__icontains = keyword)) #__icontains will search entire desc for keyword
            #we cannot perform OR operation in django..so to perfrom we use Q function
            count = len(products)
    context = {
        'products': products,
        'count' : count
    }

    return render(request, 'store/store.html',context)