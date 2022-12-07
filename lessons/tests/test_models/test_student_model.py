from django.core.exceptions import ValidationError
from django.test import TestCase
from lessons.models import User

class UserModelTestCase(TestCase):
    """Unit tests for the User model"""

    # retrieved by username="@johndoe" and "@janedoe" respectively

    fixtures = [
        'lessons/tests/fixtures/default_student_user.json',
        'lessons/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.student = User.objects.get(username="@johndoe")

    def test_valid_user(self):
        try:
            self.student.full_clean()
        except ValidationError:
            self.fail()

    def test_user_is_not_staff(self):
        self.assertFalse(self.student.is_staff)
        self.assertFalse(self.student.is_superuser)
    def test_email_must_be_unique(self):
        second_user = User.objects.get(username="@janedoe")
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
