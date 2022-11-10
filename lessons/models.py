from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
class Student(AbstractUser):
    username = models.CharField(
        max_length=30,
        unique=True
    )

    email = models.EmailField()

    first_name = models.CharField(max_length=50)

    last_name = models.CharField(max_length=50)

    password = models.CharField(max_length=100)

class Request(models.Model):
    availability = models.CharField(max_length=100, blank=False)
    #^string stating the days and times available for lessons
    num_lessons = models.PositiveIntegerField(blank=False)
    #^integer representing the number of lessons to be booked in the request
    lesson_gap = models.PositiveIntegerField(blank=False)
    #^integer representing the requested minimum days between lessons
    duration = models.PositiveIntegerField(blank=False)
    #^integer representing the desired length of booked lessons in minutes
    requestor = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        blank=False,
    )
    #^the student that made the request
    request_time = models.DateTimeField(
        auto_now=False,
        auto_now_add=True,
    )
    #^the date and time the request was made
    extra_requests = models.CharField(max_length=250)
    #^string containing any extra requests, such as teachers
