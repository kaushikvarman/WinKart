from django.shortcuts import render,redirect
from .forms import RegistrationForm
from .models import Account
from django.contrib import messages

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
            messages.success(request,'Registration successful')
            return redirect('register')
    else:
        #else it has to be get request
        form = RegistrationForm()

    context={
        'form': form,
    }
    return render(request,'accounts/register.html',context)

def login(request):
    return render(request,'accounts/login.html')

def logout(request):
    return render(request,'accounts/logout.html')