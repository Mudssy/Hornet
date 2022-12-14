from django.shortcuts import redirect
from django.conf import settings
from .models import Invoice, LessonRequest, User, BookedLesson
import datetime
import random
from django.db.models import Q

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

def login_required(view_function):
    def modified_view_function(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('log_in')
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
    record_string = f"{invoice.invoice_id},-{invoice.total_price},{student.balance},"
    student.payment_history_csv = record_string + student.payment_history_csv

    student.save()

    return invoice

def next_day_from(current_date, day):
    days = (day - current_date.weekday() + 7) % 7
    return current_date + datetime.timedelta(days=days)

def ceil_time_to_hour(time):
    if time.minute > 0:
         return time.replace(second=0, microsecond=0, minute=0, hour=time.hour+1)
    else:
        return time

def floor_time_to_hour(time):
    return time.replace(second=0,microsecond=0, minute=0, hour=time.hour)

def hourly_time_slots(start_time, end_time):
    slots = []
    for h in range(end_time.hour - start_time.hour):
        slots.append(start_time.replace(hour=start_time.hour+h))
    return slots
        
def create_booked_lessons(lesson_request):
    if not isinstance(lesson_request, LessonRequest) or not lesson_request.is_booked or lesson_request.id is None or lesson_request.num_lessons <= 0:
        return False
    

    days_and_times_for_lessons = []   ##stores eg(0,Monday,14:25:00,16:25:00)
    for num, day in lesson_request.AvailableWeekly.choices:
        if getattr(lesson_request,day.lower() + "_start_time") is not None:
            days_and_times_for_lessons.append((
                num-1,
                day,
                ceil_time_to_hour(getattr(lesson_request,day.lower()+"_start_time")),  #ceil time to next hour 
                floor_time_to_hour(getattr(lesson_request,day.lower()+"_end_time")))) #floor time to hour
    
    if len(days_and_times_for_lessons) == 0:
        return False
        

    num_lessons_booked = 0
    teacher = lesson_request.teacher
    if teacher is None:
        teacher = random.choice(list(User.objects.filter(account_type=2))) #get random teacher
    
    weeks_between_lessons = lesson_request.lesson_gap_weeks/2
    next_date = datetime.date.today()

    while(lesson_request.num_lessons > num_lessons_booked):


        found_lesson_slot = False

        for num,day,start_time,end_time in days_and_times_for_lessons:
            next_date = next_day_from(next_date,num)
            lessons_already_booked =  BookedLesson.objects.filter(teacher = teacher)

            time_slots_list = hourly_time_slots(start_time,end_time.replace(hour=end_time.hour - lesson_request.lesson_duration_hours + 1))
            if len(time_slots_list) == 0:
                return False
                
            for hour in time_slots_list:
                time_slot_available = True
                for interval in range(0,lesson_request.lesson_duration_hours):
                    interval_date_time =datetime.datetime.combine(next_date,hour)+datetime.timedelta(hours=interval)

                    for lesson_already_booked in lessons_already_booked:
                        lesson_end_time = lesson_already_booked.start_time + datetime.timedelta(hours=lesson_already_booked.duration)
                        if interval_date_time >= lesson_already_booked.start_time and interval_date_time < lesson_end_time:
                            time_slot_available = False
                            break

                    if not time_slot_available:
                        break
                                
                if time_slot_available:
                        ## time slot is available
                        book_date_time = datetime.datetime.combine(next_date,hour)
                        found_lesson_slot = True
                        break
            
            if found_lesson_slot:
                booked_lesson = BookedLesson.objects.create(
                    student = lesson_request.requestor,
                    teacher =  teacher,
                    start_time = book_date_time,
                    duration = lesson_request.lesson_duration_hours,
                )
                num_lessons_booked += 1
                next_date = next_date + datetime.timedelta(weeks=weeks_between_lessons)
                break
            else:
                next_date = next_date + datetime.timedelta(days=1)
    
    return True


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
    record_string = f"{invoice.invoice_id},{amount_paid},{student.balance},"
    student.payment_history_csv = record_string + student.payment_history_csv
    student.save()

    return invoice

def create_request(form, user):    #deprecated as form now saves its own data
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
    
    

