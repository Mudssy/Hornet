from django import forms
from django.core.validators import RegexValidator
from lessons.models import Student
from django.urls import reverse_lazy
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout,Field,HTML,Submit

class SignUpForm(forms.ModelForm):
    def __init__(self,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = StandardForm.helper(self.Meta.fields, "submit", "Sign up", "sign_up", "POST")

    class Meta:
        model = Student
        fields = ['first_name', 'last_name', 'email', 'username','new_password','confirm_password']

    new_password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(),
        validators=[RegexValidator(
            regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).*$',
            message='Password must contain an uppercase character, a lowercase '
                    'character and a number'
        )]
    )
    confirm_password = forms.CharField(label='Confirm Password', widget=forms.PasswordInput())


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

class LogInForm(forms.Form):
    def __init__(self,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = StandardForm.helper(self.Meta.fields,"submit","Log In","log_in","POST")
        
    
    class Meta:
        fields = ['username','password']
    username = forms.CharField(label="Username")
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

class StandardForm():
    def helper(fields, submitName, submitValue,form_action,form_method):
        helper = FormHelper()
        helper.form_action = reverse_lazy(form_action)
        helper.form_method = form_method

        helper.layout = Layout()

        for field in fields:
            helper.layout.append(
                Field(field,css_class = "bg-transparent text-light mb-2")
            )
        helper.layout.append(Submit(submitName,submitValue))
        return helper

