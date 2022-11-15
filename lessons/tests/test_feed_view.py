"""Tests of the feed view."""
from django.test import TestCase
from django.urls import reverse
from lessons.models import User
from lessons.tests.helpers import reverse_with_next

class FeedViewTestCase(TestCase):
    """Tests of the feed view."""

    fixtures=[
        'lessons/tests/fixtures/default_user.json',
        'lessons/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.student = User.objects.get(username='@johndoe')
        self.teacher = User.objects.get(username="@teachersmith")
        self.url = reverse('feed')

    def test_feed_url(self):
        self.assertEqual(self.url, '/feed/')

    def test_get_feed(self):
        self.client.login(username=self.student.username, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'feed.html')

    def test_student_feed_loads_student_partial(self):
        self.client.login(username=self.student.username, password="Password123")
        response = self.client.get(self.url)
        # 'STUDENT FEED' is just the initial placeholder text in the student.html partial
        self.assertContains(response, 'STUDENT FEED')
        self.assertNotContains(response, 'TEACHER FEED')

    def test_teacher_feed_loads_teacher_partial(self):
        self.client.login(username=self.teacher.username, password="Password123")
        response = self.client.get(self.url)
        # 'TEACHER FEED' is just initial placeholder text in the teacher partial. this test will fail when that
        # partial is updated. When this happens this test must be updated
        self.assertContains(response, 'TEACHER FEED')
        self.assertNotContains(response, 'STUDENT FEED')