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

