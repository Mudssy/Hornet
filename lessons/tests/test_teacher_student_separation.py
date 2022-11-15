from django.test import TestCase
from lessons.forms import SignUpForm
from django.urls import reverse
from ..models import User
from django.contrib.auth.hashers import check_password

class SignUpViewTestCase(TestCase):

    fixtures = [
        'lessons/tests/fixtures/other_users.json',
        'lessons/tests/fixtures/default_user.json'
    ]

    def setUp(self):
        self.teacher = User.objects.get(username="@teachersmith")
        self.student = User.objects.get(username="@johndoe")

    def test_teacher_student_account_types(self):
        self.assertNotEqual(self.teacher.account_type, self.student.account_type)
        self.assertEqual(self.teacher.account_type, 2)
        self.assertEqual(self.student.account_type, 1)