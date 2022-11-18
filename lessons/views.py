from django.contrib.auth import authenticate,login,logout
from django.shortcuts import render, redirect
from lessons.forms import SignUpForm, LogInForm, RequestLessonsForm
from .models import LessonRequest, User
from django.http import HttpResponseForbidden

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


def make_request(request):
    if request.method =="POST":
        if request.user.is_authenticated:
            current_user = request.user
            form = RequestLessonsForm(request.POST)
            if form.is_valid():
                LessonRequest.objects.create(
                    requestor=current_user,
                    days_available="".join(form.cleaned_data.get("days_available")),
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

def pending_requests(request):
    user = request.user
    requests = LessonRequest.objects.filter(requestor=user)
    return render(request, 'pending_requests.html', {'requests':requests,'range': range(1,len(requests))})       



