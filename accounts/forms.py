from django import forms
from .models import Account

class RegistrationForm(forms.ModelForm):

    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder':'Enter Password',
        'class':'form-control',
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder':'Confirm Password',
        'class':'form-control',
    }))

    class Meta:
        model = Account
        fields = ['first_name','last_name','phone_number','email','password']

    #to have same css style for all form attributes
    #init method will override the form fields
    #this code will loop thru all the fields in form and assign the widget
    def __init__(self,*args,**kwargs):
        super(RegistrationForm,self).__init__(*args,**kwargs)
        self.fields['first_name'].widget.attrs['placeholder'] = 'Enter First Name'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Enter last Name'
        self.fields['phone_number'].widget.attrs['placeholder'] = 'Enter phone number'
        self.fields['email'].widget.attrs['placeholder'] = 'Enter email'
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

    #To match enter password and confirm password fields
    def clean(self):
        #super class allows us to change the way the class is being saved
        #to fetch data from POST we use cleaned_data
        cleaned_data = super(RegistrationForm,self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError(
                "Password does not match!"
            )
