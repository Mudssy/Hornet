from django import forms
from django.urls import reverse
from django.test import TestCase
from lessons.forms import MakeAdminForm
from lessons.models import User

class MakeAdminFormTestCase(TestCase):
    fixtures = [
        'lessons/tests/fixtures/default_student_user.json',
        'lessons/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.url = reverse('make_admin')
        self.form_input = {
            'first_name': 'Tess',
            'last_name': 'Test',
            'email': 'tesstest@example.org',
            'username': '@tesstest',
            'new_password': 'Password123',
            'confirm_password': 'Password123'
        }
        self.director = User.objects.get(username="@director")

    def test_valid_make_admin_form_is_valid(self):
        self.form = MakeAdminForm(data=self.form_input)
        self.assertTrue(self.form.is_valid())

    def test_make_admin_form_saves(self):
        before_count = User.objects.count()
        self.client.login(username=self.director.username, password="Password123")
        self.client.post(self.url, self.form_input)
        after_count = User.objects.count()
        self.assertEqual(before_count + 1, after_count)

    def test_invalid_make_admin_form_does_not_save(self):
        self.form_input['email'] = 'bademail'
        before_count = User.objects.count()
        self.client.login(username=self.director.username, password="Password123")
        self.assertRaises(TypeError, self.client.post(self.url, self.form_input))
        after_count = User.objects.count()
        self.assertEqual(before_count, after_count)
