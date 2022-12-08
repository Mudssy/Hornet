from django import forms
from django.urls import reverse
from django.test import TestCase
from lessons.forms import OpenAccountForm
from lessons.models import User
import json

class MakeAdminFormTestCase(TestCase):
    """Unit tests of the MakeAdminForm"""

    fixtures = [
        'lessons/tests/fixtures/default_student_user.json',
        'lessons/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        with open('lessons/tests/fixtures/make_admin_form_input.json', 'r') as file:
            self.form_input = json.load(file)
        self.url = reverse('open_account')
        self.director = User.objects.get(username="@director")
        self.student = User.objects.get(username="@johndoe")


    def test_valid_open_account_form_is_valid(self):
        self.form = OpenAccountForm(data=self.form_input)
        self.assertTrue(self.form.is_valid())

    def test_invalid_form_is_invalid(self):
        self.form_input['account_type'] = 10
        form = OpenAccountForm(self.form_input)
        self.assertFalse(form.is_valid())

    def test_bound_form_does_not_create_new_object(self):
        user_count = User.objects.count()
        form = OpenAccountForm(self.form_input, instance=self.student)
        self.assertTrue(form.is_valid())
        self.client.login(username=self.director.username, password="Password123")
        edit_url = reverse('edit_account', kwargs={'user_id': self.student.id})
        self.form_input.pop('username')
        self.client.post(edit_url, self.form_input)
        after_count = User.objects.count()
        self.assertEqual(user_count, after_count)

    def test_bound_form_saves(self):
        user_count = User.objects.count()
        form = OpenAccountForm(self.form_input, instance=self.student)
        self.assertTrue(form.is_valid())
        self.client.login(username=self.director.username, password="Password123")
        edit_url = reverse('edit_account', kwargs={'user_id': self.student.id})
        self.form_input.pop('username')
        self.client.post(edit_url, self.form_input)
        after_count = User.objects.count()
        self.assertEqual(user_count, after_count)

    def test_open_account_form_saves(self):
        before_count = User.objects.count()
        self.client.login(username=self.director.username, password="Password123")
        self.client.post(self.url, self.form_input)
        after_count = User.objects.count()
        self.assertEqual(before_count + 1, after_count)

    def test_invalid_account_form_does_not_save(self):
        self.form_input['email'] = 'bademail'
        before_count = User.objects.count()
        self.client.login(username=self.director.username, password="Password123")
        self.assertRaises(TypeError, self.client.post(self.url, self.form_input))
        after_count = User.objects.count()
        self.assertEqual(before_count, after_count)
