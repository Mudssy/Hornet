from django.contrib import messages
from django.test import TestCase
from django.urls import reverse
from lessons.forms import StandardForm
from lessons.models import Student
from lessons.tests.helpers import LogInTester


class LogInViewTestCase(TestCase, LogInTester):

    fixtures = [
        'lessons/tests/fixtures/default_user.json'
    ]

    def setUp(self):
        self.url = reverse('log_in')
        self.user = Student.objects.get(username="@johndoe")

    def test_log_in_url(self):
        self.assertEqual(self.url, '/log_in/')
