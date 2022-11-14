from django.core.exceptions import ValidationError
from django.test import TestCase
from ..models import Student

class UserModelTestCase(TestCase):
    def setUp(self):
        self.student = Student.objects.create_user(
            'studentname',
            first_name='john',
            last_name='doe',
            email="john@gmail.com",
            password="Password123"
        )

    def test_valid_user(self):
        try:
            self.student.full_clean()
        except ValidationError:
            self.fail()

