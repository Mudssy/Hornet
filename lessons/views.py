from django.shortcuts import render, redirect
from lessons.forms import SignUpForm, MakeRequestForm

# Create your views here.
def home(request):
    return render(request, 'home.html')

def feed(request):
    return render(request, 'feed.html')

def sign_up(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('feed')

    else:
        form = SignUpForm()

    return render(request, 'sign_up.html', {'form': form})

def make_request(request):
    if request.method == 'POST':
        form = MakeRequestForm(request.POST)
        if form.is_valid():
            current_user=request.user
            form.save(current_user)
    else:
        form = MakeRequestForm()

    return render(request, 'make_request.html', {'form': form})
