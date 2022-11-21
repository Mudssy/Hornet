"""Tests of the feed view."""
from django.test import TestCase
from django.urls import reverse
from lessons.models import User
from lessons.tests.helpers import reverse_with_next

class FeedNavBarTestCase(TestCase):
    """Tests of the feed view."""

    fixtures=[
        'lessons/tests/fixtures/default_student_user.json',
        'lessons/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.student = User.objects.get(username='@johndoe')
        self.teacher = User.objects.get(username="@teachersmith")
        self.url = reverse('feed')

    def test_teacher_navbar_loads_correctly(self):
        self.client.login(username=self.teacher.username, password='Password123')
        response = self.client.get(self.url)
        self.assertNotContains(response, 'Pending Requests')
        self.assertNotContains(response, 'Invoices')
        self.assertContains(response, 'Lessons')

    def test_student_navbar_loads_correctly(self):
        self.client.login(username=self.student.username, password='Password123')
        response = self.client.get(self.url)
        self.assertContains(response, 'Pending Requests')
        self.assertContains(response, 'Lessons')
        self.assertContains(response, 'Invoices')
