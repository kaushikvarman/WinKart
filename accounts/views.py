from django.shortcuts import render,redirect,get_object_or_404
from .forms import RegistrationForm,UserForm,UserProfileForm
from .models import Account,UserProfile
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
#verification
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from cart.models import Cart,CartItem
from cart.views import _cart_id
import requests
from orders.models import Order,OrderProduct


# Create your views here.
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            #to fetch values from django_form we use form.clenaed_data
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split("@")[0] #we are taking username from email only including letters till @

            user = Account.objects.create_user(first_name=first_name,last_name=last_name,username=username,email=email,password=password)
            user.phone_number = phone_number
            user.save()# here basically we r retreiving data from the request.POST form
                       # then next we check if its a valid form..if its valid then we access form data and create user(we have created create_user in models.py) see code
            
            #creating user profile
            profile = UserProfile()
            profile.user_id = user.id #connecting user to userprofile
            profile.profile_picture = 'default/default-user.png'
            profile.save()

            #USER_ACTIVATION
            current_site = get_current_site(request) #getting current site
            mail_subject = "please activate your account"
            #we are using 'user':user...to use it in verification_email_template
            message = render_to_string('accounts/account_verification_email.html',{'user':user,'domain':current_site,'uid':urlsafe_base64_encode(force_bytes(user.pk)),'token':default_token_generator.make_token(user),})
            #we are encoding user id with urlsafe_base...
            to_email = email
            send_email = EmailMessage(mail_subject,message,to=[to_email])
            send_email.send()

            #messages.success(request,'Thanks for registering Now please activate your account')
            return redirect('/accounts/login/?command=verification&email='+email)
    else:
        #else it has to be get request
        form = RegistrationForm() 

    context={
        'form': form,
    }
    return render(request,'accounts/register.html',context)

def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email,password=password)
        if user is not None:
            
            #if user didnt loggedin and added items to cart
            #then after logging same items must reflect in user cart
            #this code will ensure that
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                
                if is_cart_item_exists:
                    
                    cart_item = CartItem.objects.filter(cart=cart) #it will give all the items in the cart which are assigned to cart
                    #getting product variatiomn by cart id
                    product_variation = []
                    for item in cart_item:
                            variation = item.variations.all()
                            product_variation.append(list(variation))
                            print(product_variation)
                            # item.user = user
                            # item.save()
                    #now we will get items from user to access his product variations
                    cart_items = CartItem.objects.filter(user=user)
                    product_variation2 = []
                    id = []
                    for item in cart_items:
                        variations2 = item.variations.all()
                        product_variation2.append(list(variations2))
                        id.append(item.id)
                        

                    #now we intersect this two lists to find the similar items
                    for pr in product_variation:
                        if pr in product_variation2:
                            index = product_variation2.index(pr)
                            item_id = id[index]
                            item = CartItem.objects.get(id = item_id)
                            item.quantity += 1
                            item.user = user
                            item.save()
                        else:
                            cart_item = CartItem.objects.filter(cart=cart)
                            for item in cart_item:
                                item.user = user 
                                item.save()


            except:
                pass
            auth.login(request,user)
            messages.success(request,'you are now logged in.')
            url = request.META.get('HTTP_REFERER') #it will grab the prev url 
                                                   #In our case it is "http://127.0.0.1:8000/accounts/login/?next=/cart/checkout/"
            try:
                query = requests.utils.urlparse(url).query 
                
                #query gives : next=/cart/checkout/
                params = dict(x.split('=') for x in query.split('&'))
                #params gives : {'next': '/cart/checkout/'}
                if 'next' in params:
                    nextPage = params['next']
                    return redirect(nextPage)
                
            except:
                return redirect('dashboard')
        else:
            messages.error(request,'Invalid login credentials!')
            return redirect('login')
    return render(request,'accounts/login.html')

@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request,'You are logged out.')
    return redirect('login')


def activate(request,uidb64,token):
    try:
        #uid is the primary key of user
        uid = urlsafe_base64_decode(uidb64).decode() #it will decode the uidb64 and store it in uid
        user = Account._default_manager.get(pk=uid)
    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
        user = None 
    
    if user is not None and default_token_generator.check_token(user,token): #it means we dont have any error and successfully got the user
        user.is_active = True
        user.save()
        messages.success(request,'congratulations! Your account is activated')
        return redirect('login')
    else:
        messages.error(request,'Invalid activation link')
        return redirect('register')

# chatgpt example on default_manager
# from django.db import models

# class Account(models.Model):
#     username = models.CharField(max_length=50)
#     email = models.EmailField()

# # Access the default manager
# accounts = Account._default_manager.all()  # Retrieves all Account instances
# new_account = Account._default_manager.create(username='john', email='john@example.com')  # Creates a new Account instance
# account = Account._default_manager.get(username='john')  # Retrieves an Account instance with the given username

@login_required(login_url='login')
def dashboard(request):
    orders = Order.objects.order_by('-created_at').filter(user=request.user.id,is_ordered = True)
    orders_count = orders.count()
    userprofile = UserProfile.objects.get(user_id=request.user.id)
    context = {
        'orders_count':orders_count,
        'userprofile':userprofile
    }
    return render(request,'accounts/dashboard.html',context)

def forgotpassword(request):

    if request.method =='POST':
    
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email) #__exact checks whether there is an exact email
            #reset password email
            current_site = get_current_site(request) #getting current site
            mail_subject = "please reset your password"
            #we are using 'user':user...to use it in verification_email_template
            message = render_to_string('accounts/reset_password_email.html',{'user':user,'domain':current_site,'uid':urlsafe_base64_encode(force_bytes(user.pk)),'token':default_token_generator.make_token(user),})
            #we are encoding user id with urlsafe_base...
            to_email = email
            send_email = EmailMessage(mail_subject,message,to=[to_email])
            send_email.send()

            messages.success(request,'Reset email has been sent!')
            return redirect('login')


        else:
            messages.error(request,'Account does not exist!')
            return redirect('forgotpassword')


    return render(request,'accounts/forgotpassword.html')

def resetpassword_validate(request,uidb64,token):
    
    try:
        #uid is the primary key of user
        uid = urlsafe_base64_decode(uidb64).decode() #it will decode the uidb64 and store it in uid
        user = Account._default_manager.get(pk=uid)
    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
        user = None 

    if user is not None and default_token_generator.check_token(user,token): #it means we dont have any error and successfully got the user
        request.session['uid'] = uid #to access this session later to rest the passowrd
        messages.success(request,'Reset yor password')
        return redirect('resetpassword')
    else:
        messages.error(request,'This link is expired!')
        return redirect('login')
    
def resetpassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirmpassword']

        if password == confirm_password:
            uid = request.session.get('uid') #we are getting this from line 147 in code
            user = Account._default_manager.get(pk=uid)
            user.set_password(password) #set_passord is inbuilt function of django
            user.save()
            messages.success(request,'password reset successful')
            return redirect('login')
        else:
            messages.error(request,'Password do not match')
            return redirect('resetpassword')
    else:
        return render(request,'accounts/resetpassword.html')
    
@login_required(login_url='login')
def myorders(request):
    orders = Order.objects.filter(user=request.user.id,is_ordered =True).order_by('-created_at') #'-' will give order in descending order
    context = {
        'orders':orders
    }
    return render(request,'accounts/my_orders.html',context)

@login_required(login_url='login')
def editprofile(request):
    userprofile = get_object_or_404(UserProfile,user=request.user)

     
    if request.method == 'POST':
        user_form = UserForm(request.POST,instance=request.user)
        profile_form = UserProfileForm(request.POST,request.FILES,instance=userprofile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request,'your profile has been updated.')
            return redirect('editprofile')
    else:
        user_form = UserForm(instance = request.user)
        profile_form = UserProfileForm(instance=userprofile)
    
    context =  {
        'user_form': user_form,
        'profile_form':profile_form,
        'userprofile':userprofile
    }


    return render(request,'accounts/edit_profile.html',context)

@login_required(login_url='login')
def changepassword(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        user = Account.objects.get(username__iexact=request.user.username)

        if new_password == confirm_password:
            success = user.check_password(current_password)
            if success:
                user.set_password(new_password)
                user.save()
                #auth.logout(request) ..after changinf password if we want to logout we can use this.
                #even if we do not keep..django automatically logouts us
                messages.success(request,'Password changed successfully.')
                return redirect('login')
            else:
                messages.error(request,'Invalid Current Password')
                return redirect('changepassword')
        else:
            messages.error(request,'Passwords does not match!')
            return redirect('changepassword')


    return render(request,'accounts/changepassword.html')

@login_required(login_url='login')
def orderdetail(request,order_id):
    

    #order__order_number = to access order is a foreignkey of orderproduct and order_number is order's attribute
    #using __ we can access foreign key model 
    orderdetail = OrderProduct.objects.filter(order__order_number=order_id) 
    order = Order.objects.get(order_number=order_id)

    subtotal = 0
    for i in orderdetail:
        subtotal += i.product.price * i.quantity

    context = {
        'orderdetail':orderdetail,
        'order':order,
        'subtotal':subtotal
    }
    return render(request,'accounts/orderdetail.html',context)


