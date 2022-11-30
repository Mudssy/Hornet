from django.contrib.auth import authenticate,login,logout
from django.shortcuts import render, redirect
from lessons.forms import SignUpForm, LogInForm, RequestLessonsForm, MakeAdminForm
from .models import LessonRequest, User, Invoice
from django.http import HttpResponseForbidden
from lessons.helpers import administrator_prohibited, teacher_prohibited, student_prohibited, create_invoice, director_only

# Create your views here.
def home(request):
    return render(request, 'home.html')

def feed(request):
    return render(request, 'feed.html')

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
    return render(request,"account_info.html")

@teacher_prohibited
@administrator_prohibited
def make_request(request):
    if request.method =="POST":
        if request.user.is_authenticated:
            current_user = request.user
            form = RequestLessonsForm(request.POST)
            if form.is_valid():
                LessonRequest.objects.create(
                    requestor=current_user,
                    days_available=form.cleaned_data.get("days_available"),
                    num_lessons=form.cleaned_data.get("num_lessons"),
                    lesson_gap_weeks=form.cleaned_data.get("lesson_gap_weeks"),
                    lesson_duration_hours=form.cleaned_data.get("lesson_duration_hours"),
                    # request_time = datetime.now(),
                    extra_requests=form.cleaned_data.get("extra_requests"),
                )
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

@director_only
def make_admin(request):
    if request.method=="POST":
        form=MakeAdminForm(request.POST)
        if form.is_valid():
            User.objects.create_user(
                username=form.cleaned_data.get('username'),
                first_name=form.cleaned_data.get('first_name'),
                last_name=form.cleaned_data.get('last_name'),
                email=form.cleaned_data.get('email'),
                password=form.cleaned_data.get('new_password'),
                account_type=3,
                is_staff=True,
                is_superuser=False
            )
            return redirect('feed')
    else:
        form=MakeAdminForm()
    return render(request, 'make_admin.html', {'form':form})
