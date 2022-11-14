from django import forms
from lessons.models import Student
from django.urls import reverse_lazy
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout,Field,HTML,Submit


class StandardForm(forms.ModelForm): #this class is the standard form that all forms should be the child of
    def __init__(self,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form_action = ""
        self.form_method = ""
    @property
    def helper(self):
        helper = FormHelper()
        helper.form_action = reverse_lazy(self.form_action)
        helper.form_method = self.form_method

        helper.layout = Layout()

        for field in self.Meta().fields:
            helper.layout.append(
                Field(field)
            )
        helper.layout.append(Submit('submit','Sign up'))
        return helper


class SignUpForm(StandardForm):
    def __init__(self,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form_action = "sign_up"
        self.form_method = "POST"

    class Meta:
        model = Student
        fields = ['first_name', 'last_name', 'email', 'username','new_password','confirm_password']

    new_password = forms.CharField(label='New Password', widget=forms.PasswordInput)
    confirm_password = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)


    def clean(self):
        super().clean()
        new_password = self.cleaned_data.get('new_password')
        password_confirmation = self.cleaned_data.get('confirm_password')
        if new_password  != password_confirmation:
             self.add_error('confirm_password', 'passwords do not match')

    def save(self):
        super().save(commit=False)
        user = Student.objects.create_user(
            username=self.cleaned_data.get('username'),
            first_name=self.cleaned_data.get('first_name'),
            last_name=self.cleaned_data.get('last_name'),
            email=self.cleaned_data.get('email'),
            password=self.cleaned_data.get('new_password'),
        )
        return user

class LoginForm(StandardForm):
    def __init__(self,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form_action = "log_in"
        self.form_method = "POST"
    
    class Meta:
        model = Student
        fields = ['username','password']
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

