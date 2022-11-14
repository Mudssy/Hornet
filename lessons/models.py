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

    groups = models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')

    user_permissions = models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')


class Staff(AbstractUser):
    username = models.CharField(
        max_length=30,
        unique=True
    )

    email = models.EmailField()

    first_name = models.CharField(max_length=50)

    last_name = models.CharField(max_length=50)

    password = models.CharField(max_length=100)

    staff = True

    superuser = False

    groups = models.ManyToManyField(blank=True, help_text='The groups this staff belongs to. A staff will get all permissions granted to each of their groups.', related_name='staff_set', related_query_name='user', to='auth.group', verbose_name='groups')

    user_permissions = models.ManyToManyField(blank=True, help_text='Specific permissions for this staff.', related_name='staff_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')
