from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from django.db.models import PositiveSmallIntegerField


class User(AbstractUser):
    class Account(models.IntegerChoices):
        STUDENT = 1
        TEACHER = 2
        ADMINISTRATOR = 3

    username = models.CharField(
        max_length=30,
        unique=True,
        validators=[RegexValidator(
            regex=r'^@\w{3,}$',
            message='Username must consist of @ followed by at least three alphanumericals'
        )]
    )

    email = models.EmailField(unique=True)

    first_name = models.CharField(max_length=50)

    last_name = models.CharField(max_length=50)
    account_type = PositiveSmallIntegerField(
        choices=Account.choices,
        default=Account.STUDENT
    )

    balance = models.IntegerField(default=0)

    password = models.CharField(max_length=100)

class LessonRequest(models.Model):

    class LessonGap(models.IntegerChoices):
        BIWEEKLY = 1
        WEEKLY = 2
        FORTNIGHTLY = 3
        MONTHLY = 4

    class AvailableWeekly(models.IntegerChoices):
        Monday = 1
        Tuesday = 2
        Wednesday = 3
        Thursday = 4
        Friday = 5
        Saturday = 6
        Sunday = 7

    DAYS_OF_WEEK = (
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    )

    # days of the week for which the student is available
    days_available = models.CharField(max_length=50, blank=False,default="1234567") #store available days in the week as string of numbers
                                                                #eg '126' means available Monday,Tuesday,Saturday


    num_lessons = models.PositiveIntegerField(blank=False)

    lesson_gap_weeks = models.PositiveIntegerField(
        choices=LessonGap.choices,
        default=LessonGap.WEEKLY
    )

    lesson_duration_hours = models.PositiveIntegerField(blank=False)

    requestor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=False,
    )

    # The time at which the request was made
    request_time = models.DateTimeField(
        auto_now=False,
        auto_now_add=True,
    )

    extra_requests = models.CharField(max_length=250, blank=True)

    is_booked = models.BooleanField(default=False)

class Invoice(models.Model):

    associated_student=models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=False
    )

    date_created = models.DateTimeField(
        auto_now=False,
        auto_now_add=True
    )

    invoice_id=models.CharField(
        max_length=7,
        blank=True,
        unique=True
    )

    # Information transferred from request object, for more professional invoice look
    number_of_lessons=models.PositiveIntegerField(default=1)
    lesson_duration=models.PositiveIntegerField(default=1)
    hourly_cost=models.PositiveIntegerField(default=1)
    total_price=models.PositiveIntegerField(blank=True)
    amount_paid=models.PositiveIntegerField(blank=True, default=0)
    amount_outstanding=models.PositiveIntegerField(blank=True, default=0)
    is_paid=models.BooleanField(default=False)
