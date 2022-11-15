from django.contrib import admin
from .models import Student, Request
# Register your models here.

@admin.register(Student, Request)
class UserAdmin(admin.ModelAdmin):
    pass
