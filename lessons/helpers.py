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
        num_lessons=form.cleaned_data.get("num_lessons"),
        lesson_gap_weeks=form.cleaned_data.get("lesson_gap_weeks"),
        lesson_duration_hours=form.cleaned_data.get("lesson_duration_hours"),
        # request_time = datetime.now(),
        extra_requests=form.cleaned_data.get("extra_requests"),
    )
