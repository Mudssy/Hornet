from django.shortcuts import redirect
from django.conf import settings

def administrator_prohibited(view_function):
    def modified_view_function(request):
        if request.user.account_type==3:
            return redirect('feed')
        else:
            return view_function(request)
    return modified_view_function

def teacher_prohibited(view_function):
    def modified_view_function(request):
        if request.user.account_type==2:
            return redirect('feed')
        else:
            return view_function(request)
    return modified_view_function

def student_prohibited(view_function):
    def modified_view_function(request):
        if request.user.account_type==1:
            return redirect('feed')
        else:
            return view_function(request)
    return modified_view_function