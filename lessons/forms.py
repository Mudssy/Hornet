from django import forms
from django.core.validators import RegexValidator
from lessons.models import User,LessonRequest, Invoice
from django.urls import reverse
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit, Hidden, Div, Row, Column, HTML


class SignUpForm(forms.ModelForm):
    def __init__(self,*args, **kwargs):
        super().__init__(*args, **kwargs)
        ## helper is used by crispy forms to render the form
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
    """Lesson request form, used for creating and editing lessons"""
    def __init__(self,*args, **kwargs):
        # Removing and saving this argument so it is not passed to the superclass init function
        if 'approve_permissions' in kwargs:
            approve_permissions = kwargs.pop('approve_permissions')
        else:
            approve_permissions=False

        super(RequestLessonsForm, self).__init__(*args, **kwargs)
        


        self.availability_fields = []
        for num,day in LessonRequest.AvailableWeekly.choices:
            start_variable_name =  day.lower() + "_start_time"
            end_variable_name = day.lower() + "_end_time"
            self.fields[start_variable_name] = forms.TimeField(label='', widget = forms.TimeInput(attrs={"type": "time", "value":getattr(self.instance,start_variable_name)},format=['%H:%M','%H:%M:%S']),required=False,input_formats=["%H:%M",'%H:%M:%S'])
            self.fields[end_variable_name] = forms.TimeField(label='', widget = forms.TimeInput(attrs={"type": "time","value":getattr(self.instance,end_variable_name)},format=['%H:%M','%H:%M:%S']),required = False,input_formats=["%H:%M",'%H:%M:%S'])
            self.availability_fields.append((day,start_variable_name,end_variable_name))

        if self.instance.id is None:
            #self.helper = StandardForm.helper(self.Meta.fields,"submit","Request","make_request","POST")
            self.helper = self.create_request_helper("submit","Request","make_request","POST")
        else:
            action_string = reverse('edit_request',  kwargs={'request_id': self.instance.id})
            if approve_permissions:
                self.helper = self.create_request_helper("submit", "Approve", action_string, "POST", self.instance.id)
                self.helper.layout.append(
                    Submit("edit", "Edit")
                )
            else:
                self.helper = self.create_request_helper("edit", "Edit", action_string, "POST", self.instance.id)

        self.title = "Request lessons"

        ## teacher choices needs to be updated in the innit incase teachers change
        self.fields["teacher"].choices = self.get_teacher_choices()


    
    class Meta:
        model = LessonRequest
        fields = ["teacher","num_lessons","lesson_gap_weeks","lesson_duration_hours","extra_requests"]


    def get_teacher_choices(self):
        teacher_objects = User.objects.filter(account_type = 2).values("id","username")
        teacher_choices = [(-1,"Any")]
        teacher_choices += [(teacher["id"], teacher["username"]) for teacher in teacher_objects.all()]
        return teacher_choices


    teacher = forms.ChoiceField()
    
    num_lessons = forms.IntegerField(min_value=1, max_value=20)
    lesson_gap_weeks = forms.ChoiceField(
                        choices=LessonRequest.LessonGap.choices)
    lesson_duration_hours = forms.IntegerField(min_value=1, max_value=3)
    extra_requests = forms.CharField()

    def clean(self):
        cleaned_data = super().clean()

        num_days_available= 0
        days_available = ""

        for day, start_time, end_time in self.availability_fields:
            if (cleaned_data[start_time] is not None and cleaned_data[end_time] is None) or (cleaned_data[start_time] is None and cleaned_data[end_time] is not None):
                self.add_error(start_time,"Time not set correctly")
            elif cleaned_data[start_time] is not None and cleaned_data[end_time] is not None:
                if cleaned_data[start_time] >= cleaned_data[end_time]:
                    self.add_error(start_time,"start time must be less than end time")
                else:
                    num_days_available +=1
                    days_available += str(LessonRequest.AvailableWeekly[day])
        if num_days_available == 0:
            self.add_error(None, "No times selected")
        
        if not "lesson_gap_weeks" in cleaned_data or num_days_available < 2 / float(cleaned_data["lesson_gap_weeks"]):  #this makes sure user must pick more than one day for biweekly lessons
            self.add_error("lesson_gap_weeks", "lesson gap is not possible")

        # store days_available for the model 
        cleaned_data["days_available"] = days_available


        # if any teacher is requested set teacher to none
        if int(cleaned_data["teacher"]) == -1:
            cleaned_data["teacher"] = None
        else: # otherwise set teacher by foreign key
            cleaned_data["teacher"] = User.objects.get(id = cleaned_data["teacher"])

        #NB: a random teacher is assigned on booking if none is specified
        return cleaned_data
    
    def save(self, user=None):   ##this now saved the form for both edit and new requests, user should be given if making a new request
        super().save(commit=False)
        if self.instance.id:
            for field_name in self.cleaned_data:
                setattr(self.instance,field_name,self.cleaned_data[field_name])
            self.instance.save()
        else:
            self.cleaned_data["requestor"] = user
            LessonRequest.objects.create(**self.cleaned_data)
        
        return self.instance
            

    
    def create_request_helper(self,submitName, submitValue,form_action,form_method, id=0):
        helper = FormHelper()
        helper.form_action = form_action
        helper.form_method = form_method

        helper.layout = Layout()
        helper.layout.append(
            Div(
                Div(HTML("<h5>Days</h5>"),css_class="text-center col-2 d-flex align-items-center justify-content-center"),
                Div(HTML("<h5>Start Time</h5>"),css_class="text-center col-2 d-flex align-items-center justify-content-center"),
                Div(HTML("<h5>End Time</h5>"),css_class="text-center col-2 d-flex align-items-center justify-content-center"),
                css_class = "row my-1"
            ))
        for day, start_time, end_time in self.availability_fields:
            helper.layout.append(
            Div(
                Div(HTML("<h5>" + day + "</h5>"),css_class="text-center col-2 d-flex align-items-center justify-content-center"), 
                Div(Field(start_time),css_class="col-2"),
                Div(Field(end_time),css_class="col-2"),
                css_class = "row my-1"
            ))
        
        for field in self.Meta.fields: #loop over rest of the fields in each form
            helper.layout.append(
                Field(field,css_class = "my-1")
        )
        
        

        helper.layout.append(Submit(submitName,submitValue)) # give form a submit button 
        helper.layout.append(Hidden('id', id)) # add a hidden id

        return helper
        

class OpenAccountForm(forms.ModelForm): 
    """General form used for editing accounts"""
    def __init__(self,*args,**kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.id is None:
            # Open user accounts
            self.helper = StandardForm.helper(self.Meta.fields, "submit", "Open Account", reverse("open_account"), "POST")
            self.title = "Create User"

        else:
            # Edit user accounts
            self.helper = StandardForm.helper(self.Meta.fields,"submit", "Submit", reverse("edit_account", kwargs={'user_id': self.instance.id}), "POST", self.instance.id)
            self.title = "Edit User"
            self.fields["new_password"].required = False
            self.fields["confirm_password"].required = False

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username','new_password','confirm_password', 'account_type']
    
    account_type = forms.ChoiceField(
        choices = User.Account.choices, required=True,
    )

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


    


class SubmitPaymentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = StandardForm.helper(self.Meta.fields, "submit", "Approve", reverse("submit_payment"), "POST", self.instance.invoice_id)

    class Meta:
        model = Invoice
        fields = ["amount_paid"]

    def clean(self):
        super().clean()

    amount_paid = forms.IntegerField(min_value=0, initial=0)


class StandardForm(): # helper class to create django helper easily
    def helper(fields, submitName, submitValue,form_action,form_method, id=0):
        helper = FormHelper()
        helper.form_action = form_action
        helper.form_method = form_method

        helper.layout = Layout()

        for field in fields: #loop over fields in each form
            helper.layout.append(
                Field(field,css_class = "bg-transparent text-light mb-2")
        )

        helper.layout.append(Submit(submitName,submitValue)) # give form a submit button 
        helper.layout.append(Hidden('id', id)) # add a hidden id

        return helper

    
