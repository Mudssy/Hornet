from django.shortcuts import redirect
from django.conf import settings
from .models import Invoice, LessonRequest, User, BookedLesson
import datetime

HOURLY_COST = 40

def login_prohibited(view_function):
    def modified_view_function(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('feed')
        else:
            return view_function(request, *args, **kwargs)
    return modified_view_function

def administrator_prohibited(view_function):
    def modified_view_function(request, *args, **kwargs):
        if request.user.account_type==3:
            return redirect('feed')
        else:
            return view_function(request, *args, **kwargs)
    return modified_view_function

def teacher_prohibited(view_function):
    def modified_view_function(request, *args, **kwargs):
        if request.user.account_type==2:
            return redirect('feed')
        else:
            return view_function(request, *args, **kwargs)
    return modified_view_function

def student_prohibited(view_function):
    def modified_view_function(request, *args, **kwargs):
        if request.user.account_type==1:
            return redirect('feed')
        else:
            return view_function(request, *args, **kwargs)
    return modified_view_function

def director_only(view_function):
    def modified_view_function(request, *args, **kwargs):
        if request.user.account_type==4:
            return view_function(request, *args, **kwargs)
        else:
            return redirect('feed')
    return modified_view_function

def create_invoice(lesson_request):
    """Takes a lesson request and creates an invoice object. Also updates student details"""
    if not isinstance(lesson_request, LessonRequest) or lesson_request.id is None or lesson_request.is_booked == False:
        return

    student = lesson_request.requestor
    student_invoice_id = Invoice.objects.filter(associated_student=student).count()+1
    total_cost = HOURLY_COST*lesson_request.lesson_duration_hours*lesson_request.num_lessons

    invoice = Invoice.objects.create(
        associated_student=student,
        number_of_lessons=lesson_request.num_lessons,
        lesson_duration=lesson_request.lesson_duration_hours,
        hourly_cost=HOURLY_COST,
        total_price=total_cost,
        invoice_id = str(student.id).rjust(4, '0') + "-" + (str(student_invoice_id)).rjust(4, '0'),
        amount_paid=0,
        amount_outstanding=total_cost,
        is_paid=False,
    )

    student.balance -= invoice.total_price
    record_string = f"Invoice id: {invoice.invoice_id}".ljust(20, " ") + f"-£{invoice.total_price}".ljust(5, " ") + f"Balance: {student.balance},"
    student.payment_history_csv = record_string + student.payment_history_csv

    student.save()

    return invoice


def create_booked_lessons(lesson_request):
    if not isinstance(lesson_request, LessonRequest) or lesson_request.is_booked == False or lesson_request.id is None or lesson_request.num_lessons <= 0:
        return

    counter = lesson_request.num_lessons
    teacher = lesson_request.teacher
    if teacher is None:
        teacher = list(User.objects.filter(account_type=2))[0]

    days_for_lessons = []
    for day in lesson_request.days_available:
        days_for_lessons.append(int(day) - 1)

    i = 0
    weeks_between_lessons = lesson_request.lesson_gap_weeks/2

    while(counter > i):

        today_day_of_week = datetime.datetime.now().weekday()
        request_day = days_for_lessons[0]   
        time_to_requested_day = ((request_day - today_day_of_week) + 7) % 7

        # find the next value for boooking time at least one lesson_gap ahead, and on a day mentioned in days_available
        for j in range(7):
            booking_time = datetime.datetime.today() + datetime.timedelta(weeks=i*weeks_between_lessons)  + datetime.timedelta(days=j)
            if booking_time.weekday() in days_for_lessons:
                break

        booked_lesson = BookedLesson.objects.create(
            student=lesson_request.requestor,
            teacher = teacher,
            start_time = booking_time,
            duration = lesson_request.lesson_duration_hours
        )

        i += 1
    

def update_invoice(invoice, amount_paid):
    if invoice.amount_outstanding < amount_paid:
        raise ValueError("Can not pay more than what is owed")


    amount_paid = int(amount_paid)
    invoice.amount_outstanding -= amount_paid
    invoice.amount_paid += amount_paid
    if(invoice.amount_outstanding <= 0):
        invoice.is_paid = True

    invoice.save()


    student = invoice.associated_student
    student.balance += amount_paid
    record_string = f"Invoice id: {invoice.invoice_id}".ljust(20, " ") + f"+£{amount_paid}".ljust(5, " ") + f"Balance: {student.balance},"
    student.payment_history_csv = record_string + student.payment_history_csv
    student.save()

    return invoice

def create_request(form, user):
    LessonRequest.objects.create(
        requestor=user,
        days_available=form.cleaned_data.get("days_available"),
        #availability times
        monday_start_time = form.cleaned_data.get("monday_start_time"),
        monday_end_time = form.cleaned_data.get("monday_end_time"),
        tuesday_start_time = form.cleaned_data.get("tuesday_start_time"),
        tuesday_end_time = form.cleaned_data.get("tuesday_end_time"),
        wednesday_start_time = form.cleaned_data.get("wednesday_start_time"),
        wednesday_end_time = form.cleaned_data.get("wednesday_end_time"),
        thursday_start_time = form.cleaned_data.get("thursday_start_time"),
        thursday_end_time = form.cleaned_data.get("thursday_end_time"),
        friday_start_time = form.cleaned_data.get("friday_start_time"),
        friday_end_time = form.cleaned_data.get("friday_end_time"),
        saturday_start_time = form.cleaned_data.get("saturday_start_time"),
        saturday_end_time = form.cleaned_data.get("saturday_end_time"),
        sunday_start_time = form.cleaned_data.get("sunday_start_time"),
        sunday_end_time = form.cleaned_data.get("sunday_end_time"),

        num_lessons=form.cleaned_data.get("num_lessons"),
        lesson_gap_weeks=form.cleaned_data.get("lesson_gap_weeks"),
        lesson_duration_hours=form.cleaned_data.get("lesson_duration_hours"),
        # request_time = datetime.now(),
        extra_requests=form.cleaned_data.get("extra_requests"),
        teacher = form.cleaned_data.get("teacher"),
    )


def update_request(form, request):
    pass