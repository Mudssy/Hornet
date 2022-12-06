from django import forms
from django.core.validators import RegexValidator
from lessons.models import User,LessonRequest, Invoice
from django.urls import reverse_lazy
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout,Field,HTML,Submit,Hidden,Button
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
        # Removing and saving this argument so it is not passed to the superclass init function
        if 'approve_permissions' in kwargs:
            approve_permissions = kwargs.pop('approve_permissions')
        else:
            approve_permissions=False

        super(RequestLessonsForm, self).__init__(*args, **kwargs)
        

        if self.instance.id is None:
            self.helper = StandardForm.helper(self.Meta.fields,"submit","Request","make_request","POST")
        else:
            if approve_permissions:
                self.helper = StandardForm.helper(self.Meta.fields,"submit", "Approve", "edit_request","POST", self.instance.id)
                self.helper.layout.append(
                    Submit("edit", "Edit")
                )
            else:
                self.helper = StandardForm.helper(self.Meta.fields, "edit", "Edit", "edit_request", "POST", self.instance.id)

        self.title = "Request lessons"

        ## teacher choices needs to be updated in the innit incase teachers change
        self.fields["teacher"].choices = self.get_teacher_choices()
    
    def get_teacher_choices(self):
        teacher_objects = User.objects.filter(account_type = 2).values("id","username")
        teacher_choices = [(-1,"Any")]
        teacher_choices += [(teacher["id"], teacher["username"]) for teacher in teacher_objects.all()]
        return teacher_choices


    class Meta:
        model = LessonRequest
        fields = ["days_available","teacher","num_lessons","lesson_gap_weeks","lesson_duration_hours","extra_requests"]

    days_available = forms.MultipleChoiceField(
        widget = forms.CheckboxSelectMultiple, choices=LessonRequest.AvailableWeekly.choices
    )
    teacher = forms.ChoiceField()
    
    num_lessons = forms.IntegerField(min_value=1, max_value=20)
    lesson_gap_weeks = forms.ChoiceField(
                        choices = LessonRequest.LessonGap.choices)
    lesson_duration_hours= forms.IntegerField(min_value=1, max_value=3)
    extra_requests = forms.CharField()

    def clean(self):
        cleaned_data = super().clean()
        cleaned_data["days_available"] = "".join(cleaned_data["days_available"])
        if int(cleaned_data["teacher"]) == -1:
            cleaned_data["teacher"] = None
        else:
            cleaned_data["teacher"] = User.objects.get(id = cleaned_data["teacher"])
        return cleaned_data

class MakeAdminForm(forms.ModelForm):
    def __init__(self,*args,**kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.id is None:
            self.helper = StandardForm.helper(self.Meta.fields, "submit", "Make admin", "make_admin", "POST")
            self.title = "Create Admin"
            self.fields['is_staff'].widget = forms.HiddenInput()
            self.fields['is_staff'].initial = True
            self.fields['is_superuser'].widget = forms.HiddenInput()
            self.fields['is_superuser'].initial = False
        else:
            self.helper = StandardForm.helper(self.Meta.fields,"submit", "Submit", "edit_admin", "POST", self.instance.id)
            self.title = "Edit Admin"

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username','new_password','confirm_password', 'is_staff', 'is_superuser']

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


class SubmitPaymentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = StandardForm.helper(self.Meta.fields, "submit", "Approve", "submit_payment", "POST", self.instance.invoice_id)

    class Meta:
        model = Invoice
        fields = ["amount_paid"]

    amount_paid= forms.IntegerField(min_value=0)


    def clean(self):
        super().clean()
        new_password = self.cleaned_data.get('new_password')
        password_confirmation = self.cleaned_data.get('confirm_password')
        if new_password  != password_confirmation:
             self.add_error('confirm_password', 'passwords do not match')

class StandardForm():
    def helper(fields, submitName, submitValue,form_action,form_method, id=0):
        helper = FormHelper()
        helper.form_action = reverse_lazy(form_action)
        helper.form_method = form_method

        helper.layout = Layout()

        for field in fields:
            helper.layout.append(
                Field(field,css_class = "bg-transparent text-light mb-2")
            )
        helper.layout.append(Submit(submitName,submitValue))
        helper.layout.append(Hidden('id', id))
        return helper