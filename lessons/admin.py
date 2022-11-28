"""Configuration of superadmin and staff admin interface for Hornet"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User
# Register your models here.

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'username', 'first_name', 'last_name', 'email', 'is_staff', 'is_superuser'
    ]

    class Meta:
        is_staff=True
    # Checks if admin is a superuser
#     def get_form(self, request, obj=None, **kwargs):
#         form = super().get_form(request, obj, **kwargs)
#         is_superuser = request.admin.is_superuser
#         disabled_fields = set() # holds fields which non-superadmin cannot affect
#
# #prevent admin from making other users superusers
#         if not is_superuser:
#             disabled_fields |= {
#                 'username',
#                 'is_superuser',
#                 'is_staff',
#                 'user_permissions',
#             }
#
#             readonly_fields = [
#                 'username',
#                 'date_joined',
#             ]
#
# #prevent admin from trying to make themselves superusers
#         if(
#             obj ==request.user
#             and is_superuser != True
#         ):
#             disabled_fields |= {
#                 'username',
#                 'is_superuser',
#                 'is_staff',
#                 'user_permissions',
#             }
# #iterate over all fields and mark as disabled
#         for field in disabled_fields:
#             if field in form.base_fields:
#                 form.base_fields[field].disabled = True
#
#         admin.site.register(Staff, StaffAdmin)
#         return form
