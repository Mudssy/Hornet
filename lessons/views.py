from django.contrib.auth import authenticate,login,logout
from django.shortcuts import render, redirect
from .models import LessonRequest, User, Invoice, BookedLesson
from lessons.forms import SignUpForm, LogInForm, RequestLessonsForm, SubmitPaymentForm, OpenAccountForm
from django.http import HttpResponseForbidden
from lessons.helpers import administrator_prohibited, login_prohibited, teacher_prohibited, student_prohibited, create_invoice, update_invoice, create_request, director_only, update_request, create_booked_lessons
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from django.views.generic import ListView, DetailView
from django.utils.decorators import method_decorator

# Create your views here.

def sign_up(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request,user)
            return redirect('feed')
    else:
        form = SignUpForm()

    return render(request, 'sign_up.html', {'form': form})

@login_prohibited
def log_in(request):
    if request.method == "POST":
        form = LogInForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('feed')
        form.add_error(None, "The credentials provided were incorrect")
    else:
        form = LogInForm()

    return render(request,'log_in.html',{'form':form})

def log_out(request):
    logout(request)
    return redirect('home')

def account_info(request):
    if request.user.is_authenticated:
        return render(request,"account_info.html")
    else:
        return redirect('log_in')

@teacher_prohibited
@administrator_prohibited
def make_request(request):
    if request.method =="POST":
        if request.user.is_authenticated:
            current_user = request.user
            form = RequestLessonsForm(request.POST)
            if form.is_valid():
                create_request(form, current_user)
                return redirect("feed")
        else:
            return redirect('log_in')
    else:
        form = RequestLessonsForm()

    return render(request, 'make_request.html', {'form':form})

@teacher_prohibited
def pending_requests(request):
    user = request.user
    requests = LessonRequest.objects.filter(requestor=user)
    return render(request, 'pending_requests.html', {'requests':requests,'range': range(1,len(requests))})

@teacher_prohibited
@student_prohibited
def show_all_requests(request):
    all_requests = LessonRequest.objects.all()
    return render(request, 'show_all_requests.html', {'requests': all_requests})



class EditRequestView(DetailView):
    """General form for editing a """
    def dispatch(self, request, request_id):
        self.lesson_request = LessonRequest.objects.get(id=request_id)
        return super().dispatch(request, request_id)

    def post(self, request, request_id):
        form = RequestLessonsForm(request.POST, instance=self.lesson_request)
        should_book = 'submit' in request.POST
        
        if not form.is_valid():
            form.add_error(None, "Some of these edits seem off")
            return render(request, 'edit_request.html', {'form': form, 'request_id': self.lesson_request.id})
        else:
            self.lesson_request.is_booked = should_book
            self.lesson_request.save()

            # this will just bounce if the lesson sholdnt be booked
            create_booked_lessons(self.lesson_request)
            create_invoice(self.lesson_request)
            form.save()

            return redirect('show_all_requests')

    def get(self, request, request_id):
        permissions = self.request.user.account_type >= 3
        self.form = RequestLessonsForm(instance=self.lesson_request, approve_permissions=permissions)
        return render(request, 'edit_request.html', {'form': self.form})

@director_only
def open_account(request):
    if request.method=="POST":
        form=OpenAccountForm(request.POST)
        if form.is_valid():
            staff = False
            superuser = False
            if form.cleaned_data.get("account_type") == "3":
                staff = True
            elif form.cleaned_data.get("account_type") == "4":
                superuser = True

            User.objects.create_user(
                username=form.cleaned_data.get('username'),
                first_name=form.cleaned_data.get('first_name'),
                last_name=form.cleaned_data.get('last_name'),
                email=form.cleaned_data.get('email'),
                password=form.cleaned_data.get('new_password'),
                account_type=form.cleaned_data.get('account_type'),
                is_staff=staff,
                is_superuser=superuser
            )
            return redirect('feed')
    else:
        form=OpenAccountForm()
    return render(request, 'open_account.html', {'form':form})

@director_only
def edit_account(request, user_id):
    user = User.objects.get(id=user_id)
    if request.method=="POST":
        form= OpenAccountForm(request.POST, instance=user)
        if form.is_valid():
            if form.cleaned_data.get('account_type') == "1" or form.cleaned_data.get('account_type') == "2":
                user.is_staff = False 
                user.is_superuser = False
            elif form.cleaned_data.get('account_type') == "3":
                user.is_staff = True
                user.is_superuser = False
            elif form.cleaned_data.get('account_type') == "4":
                user.is_staff = False
                user.is_superuser = True
            form.save()
            new_password = form.cleaned_data.get("new_password")  ## set the new password manually
            if new_password:
                user.set_password(new_password)  ##set_password() hashes the password
            
            user.save()
            
            return redirect("user_list", account_type = user.account_type)
    else:
        form = OpenAccountForm(instance=user)

    return render(request, 'edit_account.html', {'form': form, 'user_id': id})

def submit_payment(request):
    forms = []
    affected_form = None

    if request.method=='POST':
        invoice_id=request.POST.get('id')
        invoice = Invoice.objects.get(invoice_id=invoice_id)
        affected_form = SubmitPaymentForm(request.POST, instance=invoice)
        amount_paid = int(request.POST.get('amount_paid'))
        if amount_paid <= invoice.amount_outstanding:
            update_invoice(invoice, amount_paid)
            messages.add_message(request, messages.SUCCESS, f"Submitted {amount_paid} into {invoice.associated_student.username}'s account")
        else:
            affected_form.add_error(None, "You can not pay more than is owed for a given invoice")

    forms.append(affected_form)

    # apologies for the ugliness, this adds all instances of invoice without the one with an erroneous input
    all_invoices = Invoice.objects.filter(is_paid=False)
    for invoice in all_invoices:
        if affected_form is None or not affected_form.instance.invoice_id == invoice.invoice_id:
            form = SubmitPaymentForm(instance=(invoice))
            forms.append(form)

    return render(request, 'submit_payment.html', {'forms': forms})




class UserListView(ListView):
    """View class concerned with listing various account types"""
    model = User
    template_name='user_list.html'

    def dispatch(self, request, account_type):

        # ensure a user can never see a list of users with greater permissions than themselves
        if request.user.account_type == 4:
            # directors can see anyone
            self.account_type = account_type
        elif request.user.account_type <= account_type:
            # other users may only see user lists of users with lesser permissions than themselves
            return redirect('feed')
        else:
            self.account_type = account_type

        return super().dispatch(request, account_type)

    def get_queryset(self, *args, **kwargs):
        object_list = self.model.objects.filter(account_type=self.account_type)
        return object_list

@teacher_prohibited
@administrator_prohibited
def invoices(request):
    user = request.user
    balance = user.balance
    invoices = Invoice.objects.filter(associated_student=user)
    return render(request, 'invoices.html', {'invoices':invoices, 'balance':str(balance)})


def booked_lessons(request):
    user = request.user
    lessons = BookedLesson.objects.filter(student=user)
    return render(request, 'booked_lessons.html', {'lessons':lessons})

def delete_request(request, request_id):
    request = LessonRequest.objects.get(id=request_id)
    request.delete()

    return redirect('pending_requests')

def payment_history(request):
    payment_history_list = request.user.payment_history_csv.split(",")
    return render(request, 'payment_history.html', {'payments': payment_history_list})

def user_payment_history(request, user_id):
    user = User.objects.get(id=user_id)
    payment_history_list = user.payment_history_csv.split(",")
    return render(request, 'payment_history.html', {'payments': payment_history_list, 'user': user})

@student_prohibited
@teacher_prohibited
def delete_user(request, user_id):
    user=User.objects.get(id=user_id)
    user.delete()
    return redirect("user_list", account_type = user.account_type)

def home(request):
    return render(request, 'home.html')

def feed(request):
    if request.user.is_authenticated:
        return render(request, 'feed.html')
    else:
        return redirect('log_in')