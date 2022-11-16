from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from django.db.models import PositiveSmallIntegerField


# Create your models here.


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

    password = models.CharField(max_length=100)

class LessonRequest(models.Model):

    availability = models.CharField(max_length=100, blank=False)

    num_lessons = models.PositiveIntegerField(blank=False)

    lesson_gap = models.PositiveIntegerField(blank=False)

    duration = models.PositiveIntegerField(blank=False)

    requestor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=False,
    )

    request_time = models.DateTimeField(
        auto_now=False,
        auto_now_add=True,
    )

    extra_requests = models.CharField(max_length=250)

