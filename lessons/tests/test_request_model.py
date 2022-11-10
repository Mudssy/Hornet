from django.core.exceptions import ValidationError
from django.test import TestCase
from ..models import Student, Request

class RequestModelTestCase(TestCase):
    def setUp(self):
        self.student = Student.objects.create_user(
            'studentname',
            first_name='john',
            last_name='doe',
            email="john@gmail.com",
            password="Password123"
        )
        self.request = Request.objects.create(
            availability='Available any weekday from 9am to 3pm',
            num_lessons=4,
            lesson_gap=7,
            duration=60,
            requestor=self.student,
            extra_requests='I want to practice music theory with Mrs Doe at least once, and practice the clarinet at least twice'
        )

    def test_valid_user(self):
        try:
            self.request.full_clean()
        except(ValidationError):
            self.fail()
