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
    # ======================
    # FOR LIST VIEW OF USERS
    # ======================
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

    def test_user_cannot_view_directors(self):
        self.client.login(username=self.student.username, password="Password123")
        url = reverse('user_list', kwargs={'account_type': 2})
        response = self.client.get(url)
        redirect_url = reverse('feed')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    # ======================
    # FOR LIST VIEW OF DIRECTORS
    # ======================

    def test_director_view_directors(self):
        self.client.login(username=self.director.username, password="Password123")
        url = reverse('user_list', kwargs={'account_type': 4})
        response = self.client.get(url)
        self.assertContains(response, self.director)

    def test_director_view_users(self):
        self.client.login(username=self.director.username, password="Password123")
        url = reverse('user_list', kwargs={'account_type': 1})
        response = self.client.get(url)
        for user in User.objects.filter(account_type=1):
            self.assertContains(response, user)

    def test_director_view_teacher(self):
        self.client.login(username=self.director.username, password="Password123")
        url = reverse('user_list', kwargs={'account_type': 2})
        response = self.client.get(url)
        for user in User.objects.filter(account_type=2):
            self.assertContains(response, user)

    def test_director_view_admins(self):
        self.client.login(username=self.director.username, password="Password123")
        url = reverse('user_list', kwargs={'account_type': 3})
        response = self.client.get(url)
        for user in User.objects.filter(account_type=3):
            self.assertContains(response, user)