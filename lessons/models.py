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


