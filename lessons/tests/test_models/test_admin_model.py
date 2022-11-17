"""Test of the admin model"""

from django.core.exceptions import ValidationError
from django.test import TestCase
# from ..admin import StaffAdmin
# from ..models import Staff
# from django.contrib import admin
#
#
# class AdminTestCase(TestCase):
#
# # TODO: set up superadmin
#     def setUp(self):
#         self.staff = Staff.objects.create_user(
#             'staff_name',
#             first_name = 'Staffy',
#             last_name = 'McStafferson',
#             email = "staff@gmail.com",
#             password = "StaffPassword123",
#         )
#
#     def test_valid_admin(self):
#         try:
#             self.staff.full_clean()
#         except(ValidationError):
#             self.fail()
#
#     def test_admin_is_staff(self):
#         self.assertTrue(self.staff)
#         self.assertFalse(self.staff)

#TODO: test that admin can be made supervisor
