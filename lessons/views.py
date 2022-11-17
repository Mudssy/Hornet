from django.contrib.auth import authenticate,login,logout
from django.shortcuts import render, redirect
from lessons.forms import SignUpForm, LogInForm, RequestLessonsForm
from .models import LessonRequest, User

# Create your views here.
def home(request):
    return render(request, 'home.html')

def feed(request):
    user = request.user
    requests = LessonRequest.objects.filter(requestor=user)
    if user.account_type == 1:
        return render(request, 'student_feed.html', {'requests':requests})
    else:
        return render(request, 'teacher_feed.html',{'requests':requests})

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
    if request.method == "POST":
        form = RequestLessonsForm(request.POST)
    else:
        form = RequestLessonsForm()
    return render(request, 'make_request.html', {'form':form})

