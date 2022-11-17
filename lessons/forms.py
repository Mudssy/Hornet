from django import forms
from django.core.validators import RegexValidator
from lessons.models import User,LessonRequest
from django.urls import reverse_lazy
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout,Field,HTML,Submit
from datetime import datetime

class SignUpForm(forms.ModelForm):
    def __init__(self,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = StandardForm.helper(self.Meta.fields, "submit", "Sign up", "sign_up", "POST")
        self.title = "Sign up" 

    class Meta:
        model = User
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
        user = User.objects.create_user(
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
        self.title = "Login"
        
    
    class Meta:
        fields = ['username','password']
    username = forms.CharField(label="Username")
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

class RequestLessonsForm(forms.ModelForm):
    def __init__(self,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = self.create_custom_helper()
        self.title = "Request lessons"
    
    class Meta:
        model = LessonRequest
        fields = ["days_available","num_lessons","lesson_gap_weeks","lesson_duration_hours","extra_requests"]

    days_available = forms.MultipleChoiceField(
        widget = forms.CheckboxSelectMultiple, choices=LessonRequest.AvailableWeekly.choices
    )
    num_lessons = forms.IntegerField(min_value=1, max_value=20)
    lesson_gap_weeks = forms.ChoiceField(
                        choices = LessonRequest.LessonGap.choices)
    lesson_duration_hours= forms.IntegerField(min_value=1, max_value=3)
    extra_requests = forms.CharField()

    def clean(self):
        super().clean()
    def save(self):
        super().save(commit=False)
        
        request = LessonRequest.objects.create(

            days_available = "".join(self.cleaned_data.get("days_available")),
            num_lessons = self.cleaned_data.get("num_lessons"),
            lesson_gap_weeks = self.cleaned_data.get("lesson_gap_weeks"),
            lesson_duration_hours = self.cleaned_data.get("lesson_duration_hours"),
            #request_time = datetime.now(),
            extra_requests = self.cleaned_data.get("extra_requests"),


        )
        return request




    def create_custom_helper(self):
        helper = FormHelper()
        helper.layout = Layout()

        #helper.layout.append(HTML("Days available"))

        for field in self.Meta.fields:
            helper.layout.append(
                Field(field)
            )

        return helper





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

