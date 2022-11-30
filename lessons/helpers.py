from django.shortcuts import redirect
from django.conf import settings
from .models import Invoice, LessonRequest, User

HOURLY_COST = 40



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

def director_only(view_function):
    def modified_view_function(request):
        if request.user.account_type==4:
            return view_function(request)
        else:
            return redirect('feed')
    return modified_view_function

def create_invoice(lesson_request):
    if not isinstance(lesson_request, LessonRequest) or lesson_request.id is None or lesson_request.is_booked == False:
        return

    student = lesson_request.requestor
    student_invoice_id = Invoice.objects.filter(associated_student=student).count()+1


    invoice = Invoice.objects.create(
        associated_student=student,
        number_of_lessons=lesson_request.num_lessons,
        lesson_duration=lesson_request.lesson_duration_hours,
        hourly_cost=HOURLY_COST,
        total_price=HOURLY_COST*lesson_request.lesson_duration_hours*lesson_request.num_lessons,
        invoice_id = str(student.id).rjust(4, '0') + "-" + (str(student_invoice_id)).rjust(4, '0')
    )

    student.balance -= invoice.total_price
    student.save()
