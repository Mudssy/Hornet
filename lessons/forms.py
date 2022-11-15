from django import forms
from lessons.models import Student, Request

class SignUpForm(forms.ModelForm):
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

class MakeRequestForm(forms.ModelForm):
    class Meta:
        model=Request
        fields = ['availability', 'num_lessons', 'lesson_gap', 'duration', 'requestor', 'request_time', 'extra_requests', 'request_fulfilled']
        exclude = ['requestor', 'request_time', 'request_fulfilled']
        widgets = {
            'availability': forms.Textarea(),
            'extra_requests': forms.Textarea()
        }

    def save(self, student):
        super().save(commit=False)
        request = Request.objects.create(
            availability=self.cleaned_data.get('availability'),
            num_lessons=self.cleaned_data.get('num_lessons'),
            lesson_gap=self.cleaned_data.get('lesson_gap'),
            duration=self.cleaned_data.get('duration'),
            requestor=student,
            extra_requests=self.cleaned_data.get('extra_requests'),
        )
