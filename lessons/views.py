from django.contrib.auth import authenticate,login,logout
from django.shortcuts import render, redirect
from lessons.forms import SignUpForm, LogInForm, RequestLessonsForm, SubmitPaymentForm
from .models import LessonRequest, User, Invoice
from django.http import HttpResponseForbidden
from lessons.helpers import administrator_prohibited, teacher_prohibited, student_prohibited, create_invoice, update_invoice, create_request
from django.contrib import messages
from django.urls import reverse

# Create your views here.
def home(request):
    return render(request, 'home.html')

def feed(request):
    if request.user.is_authenticated:
        return render(request, 'feed.html')
    else:
        return redirect('log_in')

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

def log_in(request):
    if request.method == "POST":
        form = LogInForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username,password=password)
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

def booked_lessons(request):
    user = request.user
    requests = LessonRequest.objects.filter(requestor=user)
    return render(request, 'booked_lessons.html', {'requests':requests})

@teacher_prohibited
@student_prohibited
def show_all_requests(request):
    all_requests = LessonRequest.objects.all()
    return render(request, 'show_all_requests.html', {'requests': all_requests})


@student_prohibited
@teacher_prohibited
def edit_request(request):
    if request.method=="POST":
        id=request.POST.get('request_id')
        lesson_request = LessonRequest.objects.get(id=id)
        lesson_request.is_booked=True
        form = RequestLessonsForm(request.POST, instance=lesson_request)
        if form.is_valid():
            form.save()
            create_invoice(lesson_request)
            return redirect('show_all_requests')
    else:
        lesson_request = LessonRequest.objects.get(id=request.GET.get('request_id'))
        form = RequestLessonsForm(instance=lesson_request)
        id = request.GET.get('request_id')

    return render(request, 'edit_request.html', {'form': form, 'request_id': id})



@teacher_prohibited
@administrator_prohibited
def invoices(request):
    user = request.user
    balance = user.balance
    print(balance)
    invoices = Invoice.objects.filter(associated_student=user)
    return render(request, 'invoices.html', {'invoices':invoices, 'balance':str(balance)})


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
