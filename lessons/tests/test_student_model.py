from django.core.exceptions import ValidationError
from django.test import TestCase
from ..models import Student

class UserModelTestCase(TestCase):

    # retrieved by username="@johndoe" and "@janedoe" respectively

    fixtures = [
        'lessons/tests/fixtures/default_user.json',
        'lessons/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.student = Student.objects.get(username="@johndoe")
        # self.student = Student.objects.create_user(
        #     '@studentname',
        #     first_name='john',
        #     last_name='doe',
        #     email="john@gmail.com",
        #     password="Password123"
        # )

    def test_valid_user(self):
        try:
            self.student.full_clean()
        except ValidationError:
            self.fail()

    def test_email_must_be_unique(self):
        second_user = Student.objects.get(username="@janedoe")
        self.student.email = second_user.email
        self._assert_user_is_invalid()

    def _assert_user_is_valid(self):
        try:
            self.student.full_clean()
        except (ValidationError):
            self.fail('Test user should be valid')

    def _assert_user_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.student.full_clean()