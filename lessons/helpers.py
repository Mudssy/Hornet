from django.shortcuts import redirect
from django.conf import settings
from .models import Invoice, LessonRequest, User
import datetime

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

def create_booked_lessons(lesson_request):
    if not isinstance(lesson_request, LessonRequest) or lesson_request.is_booked == True or lesson_request.id is None or lesson_request.num_lessons <= 0:
        return
    counter = lesson_request.num_lessons
    date = datetime(2020, 2, 20)
    while(counter > 0):
        booked_lesson = BookedLesson.objects.create(
            associated_lesson_request = lesson_request,
            days_available = lesson_request.days_available,
            num_lessons = lesson_request.num_lessons,
            lesson_gap_weeks = lesson_request.lesson_gap_weeks,
            lesson_duration_hours = lesson_request.lesson_duration_hours,
            extra_requests = lesson_request.extra_requests,
            teacher = lesson_request.teacher,
            lesson_date = date
        )
        date += timedelta(days=1)

        counter = counter - 1
    lesson_request.is_booked = True
