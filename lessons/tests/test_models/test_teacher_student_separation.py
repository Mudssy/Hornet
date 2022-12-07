from django.test import TestCase
from lessons.forms import SignUpForm
from django.urls import reverse
from lessons.models import User
from django.contrib.auth.hashers import check_password

class SignUpViewTestCase(TestCase):
    """Unit tests of the separation between teacher and student"""

    fixtures = [
        'lessons/tests/fixtures/other_users.json',
        'lessons/tests/fixtures/default_student_user.json'
    ]

    def setUp(self):
        self.teacher = User.objects.get(username="@teacher")
        self.student = User.objects.get(username="@johndoe")

    def test_teacher_student_account_types(self):
        self.assertNotEqual(self.teacher.account_type, self.student.account_type)
        self.assertEqual(self.teacher.account_type, 2)
        self.assertEqual(self.student.account_type, 1)

    def test_teacher_cannot_make_request(self):
        self.client.login(username=self.teacher.username, password='Password123')
        request_url = reverse('make_request')
        response = self.client.get(request_url, follow=True)
        response_url = reverse('feed')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'feed.html')

    def test_teacher_cannot_see_pending_requests(self):
        self.client.login(username=self.teacher.username, password='Password123')
        request_url = reverse('pending_requests')
        response = self.client.get(request_url, follow=True)
        response_url = reverse('feed')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'feed.html')
