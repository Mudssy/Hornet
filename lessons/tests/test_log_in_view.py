from django.contrib import messages
from django.test import TestCase
from django.urls import reverse
from lessons.forms import LogInForm
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

    def test_log_in_with_blank_password(self):
        form_input = { 'username': '@johndoe', 'password': '' }
        response = self.client.post(self.url, form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertTrue(form.is_bound)
        self.assertFalse(self._is_logged_in())
        messages_list = list(form.errors)
        self.assertEqual(len(messages_list), 2)

    def test_log_in_with_incorrect_password(self):
        form_input = { 'username': '@johndoe', 'password': 'NotMyPassword' }
        response = self.client.post(self.url, form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertTrue(form.is_bound)
        self.assertFalse(self._is_logged_in())
        messages_list = list(form.errors)
        self.assertEqual(len(messages_list), 1)

    def test_log_in_with_incorrect_username(self):
        form_input = { 'username': '@johndoeseph', 'password': 'Password123' }
        response = self.client.post(self.url, form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertTrue(form.is_bound)
        self.assertFalse(self._is_logged_in())
        messages_list = list(form.errors)
        self.assertEqual(len(messages_list), 1)

    def test_successful_log_in_redirects(self):
        redirect_url=reverse('feed')
        form_input = { 'username': '@johndoe', 'password': 'Password123' }
        response = self.client.post(self.url, form_input, follow=True)
        self.assertTrue(self._is_logged_in())
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)


