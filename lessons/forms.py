from django import forms
from lessons.models import Student
from django.urls import reverse_lazy
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

class SignUpForm(forms.ModelForm):

    def __init__(self,*args,**kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_action = reverse_lazy('sign_up')
        self.helper.form_method = "POST"
        self.helper.add_input(Submit('submit','Sign up'))

    class Meta:
        model = Student
        fields = ['first_name', 'last_name', 'email', 'username']

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