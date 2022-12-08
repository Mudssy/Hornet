from django.contrib.auth.hashers import check_password
from django import forms
from django.urls import reverse
from django.test import TestCase
from lessons.forms import SignUpForm, RequestLessonsForm
from lessons.models import User, LessonRequest, Invoice



class UserListFormTestCase(TestCase):
    

    fixtures = [
        'lessons/tests/fixtures/default_student_user.json',
        'lessons/tests/fixtures/other_users.json'
    ]


    def setUp(self):
        self.student = User.objects.get(username="@johndoe")
        self.teacher = User.objects.get(username="@teacher")
        self.admin = User.objects.get(username="@administrator")
        self.director = User.objects.get(username="@director")
        self.url = reverse('user_list', kwargs={'account_type': 1})



    def test_url(self):
        self.assertEqual(self.url, '/user_list/1')

    def test_user_in_user_list(self):
        self.client.login(username=self.admin.username, password="Password123")
        response = self.client.get(self.url)

        self.assertContains(response, self.student)
    
    def test_teacher_not_in_user_list(self):
        self.client.login(username=self.admin.username, password="Password123")
        response = self.client.get(self.url)

        self.assertNotContains(response, self.teacher)

    def test_director_not_in_user_list(self):
        self.client.login(username=self.admin.username, password="Password123")
        response = self.client.get(self.url)

        self.assertNotContains(response, self.director)

