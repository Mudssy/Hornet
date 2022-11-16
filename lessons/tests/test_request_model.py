from django.core.exceptions import ValidationError
from django.test import TestCase
from ..models import User, Request

class RequestModelTestCase(TestCase):
    """Unit tests for the request model"""

    def setUp(self):
        self.student = User.objects.create_user(
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

    def test_student_can_have_multiple_requests(self):
        test_request = Request.objects.create(
            availability='dummy',
            num_lessons=5,
            lesson_gap=8,
            duration=45,
            requestor=self.student,
            extra_requests='dummy2',
        )
        self._assert_request_is_valid()

    def test_availability_can_be_100_characters(self):
        self.request.availability='x'*100
        self._assert_request_is_valid()

    def test_availability_can_not_be_101_characters(self):
        self.request.availability='x'*101
        self._assert_request_is_invalid()

    def _assert_request_is_valid(self):
        try:
            self.request.full_clean()
        except(ValidationError):
            self.fail('Test should be valid')

    def _assert_request_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.request.full_clean()
