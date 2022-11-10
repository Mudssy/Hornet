"""Configuration of superadmin and staff admin interface for Hornet"""
from typing import Set
from django.contrib import admin
from .models import Student
# Register your models here.

"""Configuration of admin interface"""
@admin.register(Student)
class UserAdmin(admin.ModelAdmin):
    #Checks if user is a superuser
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        is_superuser = request.user.is_superuser
        disabled_fields = set() #holds fields to disable for non-superusers

        if not is_superuser:
            disabled_fields |= {
                'username',
                'is_superuser'
            }
        return form

    readonly_fields = [
        'username',
    ]
