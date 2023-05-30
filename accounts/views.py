from django.shortcuts import render,redirect
from .forms import RegistrationForm
from .models import Account
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
            auth.login(request,user)
            messages.success(request,'you are now logged in.')
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
    return render(request,'accounts/dashboard.html')

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


