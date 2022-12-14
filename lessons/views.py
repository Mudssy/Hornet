from django.contrib.auth import authenticate,login,logout
from django.shortcuts import render, redirect
from .models import LessonRequest, User, Invoice, BookedLesson
from lessons.forms import SignUpForm, LogInForm, RequestLessonsForm, SubmitPaymentForm, OpenAccountForm
from django.http import HttpResponseForbidden
from lessons.helpers import administrator_prohibited, login_prohibited, teacher_prohibited, student_prohibited, create_invoice, update_invoice, create_request, director_only, create_booked_lessons
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from django.views.generic import ListView, DetailView
from django.utils.decorators import method_decorator
from datetime import datetime
from csv import reader

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

@teacher_prohibited
@administrator_prohibited
def make_request(request):
    if request.method =="POST":
        if request.user.is_authenticated:
            current_user = request.user
            form = RequestLessonsForm(request.POST)
            if form.is_valid():
                form.save(user = current_user)
                return redirect("feed")
        else:
            return redirect('log_in')
    else:
        form = RequestLessonsForm()

    return render(request, 'make_request.html', {'form':form})


class EditRequestView(DetailView):
    """General form for editing a request, used by students and admins"""
    def dispatch(self, request, request_id):
        self.lesson_request = LessonRequest.objects.get(id=request_id)
        self.permissions = self.request.user.account_type >= 3
        return super().dispatch(request, request_id)

    def post(self, request, request_id):
        form = RequestLessonsForm(request.POST, instance=self.lesson_request, approve_permissions=self.permissions)
        should_book = 'submit' in request.POST

        if not form.is_valid():
            form.add_error(None, "Some of these edits seem off")
            return render(request, 'edit_request.html', {'form': form, 'request_id': self.lesson_request.id})
        else:

            # this will just bounce if the lesson sholdnt be booked
            self.lesson_request.is_booked = should_book
            create_booked_lessons(self.lesson_request)
            create_invoice(self.lesson_request)

            self.lesson_request.save()
            form.save()

            return redirect('show_all_requests')

    def get(self, request, request_id):
        self.form = RequestLessonsForm(instance=self.lesson_request, approve_permissions=self.permissions)
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




class SubmitPayment(DetailView):
    """View class for admin to submit payments into student accounts"""
    def post(self, request):
        # extract info from post request
        edit_id = request.POST.get('id')
        amount_paid = int(request.POST.get("amount_paid"))

        candidate_invoice = Invoice.objects.get(invoice_id=edit_id)
        all_invoices = filter(lambda x: candidate_invoice.invoice_id != x.invoice_id, Invoice.objects.all())

        forms = []
        for invoice in all_invoices:
            forms.append(SubmitPaymentForm(instance = invoice))

        # partial payment
        if amount_paid < candidate_invoice.amount_outstanding:
            update_invoice(candidate_invoice, amount_paid)
            messages.add_message(request, messages.SUCCESS,
                f"Submitted {amount_paid} into {candidate_invoice.associated_student.username}'s account")
            forms.append(SubmitPaymentForm(request.POST, instance=candidate_invoice))
        # full payment
        elif amount_paid == candidate_invoice.amount_outstanding:
            update_invoice(candidate_invoice, amount_paid)
            messages.add_message(request, messages.SUCCESS,
                f"Invoice id: {edit_id} for user: {candidate_invoice.associated_student.username} has been settled")

        else:
            # erroneous payment
            error_form = SubmitPaymentForm(request.POST, instance=candidate_invoice)
            error_form.add_error('amount_paid', 'Payment exceeds amount outstanding')
            messages.add_message(request, messages.ERROR,
                                 f"Cannot pay over what is owed: \n"
                                 f"Tried to pay {candidate_invoice.amount_outstanding} into invoice {edit_id} when {candidate_invoice.amount_outstanding} was owed")
            forms.append(error_form)

        return render(request, 'submit_payment.html', {'forms': forms})

    def get(self, request):
        forms = []
        for invoice in Invoice.objects.all():
            forms.append(SubmitPaymentForm(instance=invoice))

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


def account_info(request):
    if request.user.is_authenticated:
        return render(request,"account_info.html")
    else:
        return redirect('log_in')

@teacher_prohibited
@administrator_prohibited
def invoices(request):
    user = request.user
    balance = user.balance
    invoices = Invoice.objects.filter(associated_student=user)
    return render(request, 'invoices.html', {'invoices':invoices, 'balance':str(balance)})

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


def booked_lessons(request):
    user = request.user
    if user.account_type == 1:
        lessons = BookedLesson.objects.filter(student=user)
    else:
        lessons = BookedLesson.objects.filter(teacher=user)
    return render(request, 'booked_lessons.html', {'lessons':lessons})

def delete_request(request, request_id):
    request = LessonRequest.objects.get(id=request_id)
    request.delete()

    return redirect('pending_requests')

def payment_history(request):
    user = request.user
    history_list = user.payment_history_csv.split(',')
    payment_history_table = []
    # decomposes payment_history_csv to a table that can be displayed in the view
    i = 0
    while i + 3 < len(history_list):
        payment_history_table.append(history_list[i:i + 3])
        i += 3
    return render(request, 'payment_history.html', {'payments': payment_history_table})


@teacher_prohibited
def user_payment_history(request, user_id):
    user = User.objects.get(id=user_id)
    history_list = user.payment_history_csv.split(',')
    payment_history_table = [[]]


    i = 0
    while i + 3 <= len(history_list):
        payment_history_table.append(history_list[i:i+3])
        i += 3
    return render(request, 'payment_history.html', {'payments': payment_history_table, 'user': user})

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
