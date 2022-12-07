"""Tests of the feed view."""
from django.test import TestCase
from django.urls import reverse
from lessons.models import User
from lessons.tests.helpers import reverse_with_next

class FeedViewTestCase(TestCase):
    """Tests of the feed view."""

    fixtures=[
        'lessons/tests/fixtures/default_student_user.json',
        'lessons/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.student = User.objects.get(username='@johndoe')
        self.teacher = User.objects.get(username="@teacher")
        self.url = reverse('feed')

    def test_feed_url(self):
        self.assertEqual(self.url, '/feed/')

    def test_get_student_feed(self):
        self.client.login(username=self.student.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_get_teacher_feed(self):
        self.client.login(username=self.teacher.username, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
    
    def test_client_must_be_logged_in(self):
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, reverse('log_in'), status_code=302, target_status_code=200)

