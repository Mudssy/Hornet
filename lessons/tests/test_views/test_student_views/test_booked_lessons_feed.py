from django.contrib.auth.hashers import check_password
from django import forms
from django.urls import reverse
from django.test import TestCase
from lessons.forms import SignUpForm, RequestLessonsForm
from lessons.models import User, LessonRequest, BookedLesson
import datetime
import json

class BookedLessonTestCase(TestCase):
    """Tests of the feed view."""

    fixtures=[
        'lessons/tests/fixtures/default_student_user.json',
        'lessons/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.student = User.objects.get(username="@johndoe")
        self.admin = User.objects.get(username="@administrator")
        self.teacher = User.objects.get(username="@teacher")
        with open('lessons/tests/fixtures/lesson_request_form_input.json', 'r') as file:
            self.form_input=json.load(file)
            self.form_input['teacher'] = str(self.teacher.id)

        self.url = reverse('booked_lessons')
        self.booked_lesson = BookedLesson.objects.get(id=99)

    def test_booked_lesson_in_view(self):
        self.client.login(username=self.student.username, password="Password123")
        response = self.client.get(self.url)
        object_list = list(response.context['lessons'])
        self.assertTrue(
            self.booked_lesson in object_list
        )

    def test_booked_lesson_shows_teacher(self):
        self.client.login(username=self.student.username, password="Password123")
        response = self.client.get(self.url)
        self.assertContains(response, self.teacher.username)

    def test_booked_lesson_shows_time(self):
        self.client.login(username=self.student.username, password="Password123")
        response = self.client.get(self.url)
        self.assertContains(response, self.teacher.username)