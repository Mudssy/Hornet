from django import forms
from models import Student

class SignUpForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['first_name', 'last_name', 'user_name', 'new_password', 'confirm_password']

    first_name = forms.CharField(label='First name', max_length=50)
    last_name = forms.CharField(label='Last name', max_length=50)
    username = forms.CharField(label='Username', max_length=30)
    email = forms.EmailField(label='Email')
    new_password = forms.CharField(label='New Password', widget=forms.PasswordInput)
    confirm_password = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)
