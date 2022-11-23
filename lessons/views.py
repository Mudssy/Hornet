from django.contrib.auth import authenticate,login,logout
from django.shortcuts import render, redirect
from lessons.forms import SignUpForm, LogInForm
from .models import LessonRequest, User
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import group_required

# Create your views here.
def home(request):
    return render(request, 'home.html')

def feed(request):
    user = request.user
    requests = LessonRequest.objects.filter(requestor=user)
    if user.account_type == 1:
        return render(request, 'student_feed.html', {'requests':requests})
    else:
        return render(request, 'teacher_feed.html')

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
    return render(request, 'make_request.html')

#associate user to administrator group
def add_to_admin_group(request):
    admin_group = Group.objects.get(account_type= 3)
    request.user.groups.add(admin_group)
    return HttpResponse("Successfully added")

#associate user to director group
def add_to_director_group(request):
    director_group = Group.objects.get(account_type= 4)
    request.user.groups.add(director_group)
    return HttpResponse("Successfully added")

#associate user to teacher group
def add_to_teacher_group(request):
    teacher_group = Group.objects.get(account_type= 2)
    request.user.groups.add(teacher_group)
    return HttpResponse("Successfully added")
