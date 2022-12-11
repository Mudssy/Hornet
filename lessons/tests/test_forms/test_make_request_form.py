from django.contrib.auth.hashers import check_password
from django import forms
from django.urls import reverse
from django.test import TestCase
from lessons.forms import SignUpForm, RequestLessonsForm
from lessons.models import User, LessonRequest
import json

class RequestFormTestCase(TestCase):
    """Unit tests of the RequestLessonsForm"""

    fixtures = [
        'lessons/tests/fixtures/default_student_user.json',
        'lessons/tests/fixtures/other_users.json'
    ]


    def setUp(self):
        self.url=reverse('make_request')
        self.student = User.objects.get(username="@johndoe")
        self.teacher = User.objects.get(username="@teacher")
        with open('lessons/tests/fixtures/lesson_request_form_input.json', 'r') as file:
            self.form_input=json.load(file)
            self.form_input['teacher'] = str(self.teacher.id)

    def test_valid_form_is_valid(self):
        self.form = RequestLessonsForm(data=self.form_input)
        self.assertTrue(self.form.is_valid())

    def test_form_no_teacher(self):
        self.form_input['teacher'] = -1
        form = RequestLessonsForm(self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_allows_20_lessons(self):
        self.form_input['num_lessons'] = 20
        form=RequestLessonsForm(self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_disallows_21_lessons(self):
        self.form_input['num_lessons'] = 21
        form=RequestLessonsForm(self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_lesson_gap_can_be_monthly(self):
        self.form_input['lesson_gap_weeks'] = 8
        form = RequestLessonsForm(self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_lesson_gap_cannot_be_7(self):
        self.form_input['lesson_gap_weeks'] = 7
        form = RequestLessonsForm(self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_computes_days_available_correctly(self):
        form = RequestLessonsForm(self.form_input)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["days_available"], '1')

    def test_form_saves(self):
        before_count = LessonRequest.objects.count()
        self.client.login(username=self.student.username, password="Password123")
        self.client.post(self.url, self.form_input)
        after_count = LessonRequest.objects.count()
        self.assertEqual(before_count + 1, after_count)

    def test_invalid_form_doesnt_save(self):
        self.form_input['lesson_duration_hours'] = 22
        before_count = LessonRequest.objects.count()
        self.client.login(username=self.student.username, password="Password123")
        self.assertRaises(TypeError, self.client.post(self.url, self.form_input))
        after_count = LessonRequest.objects.count()
        self.assertEqual(before_count, after_count)

    def test_form_saves_correctly(self):
        self.client.login(username=self.student.username, password="Password123")
        self.client.post(self.url, self.form_input)
        saved_form = LessonRequest.objects.get(requestor=self.student, monday_start_time='14:00')
        self.assertEqual(saved_form.requestor, self.student)
        self.assertEqual(saved_form.days_available, '1') #1 being monday
        self.assertEqual(saved_form.lesson_gap_weeks, 2)
        self.assertEqual(saved_form.num_lessons, self.form_input['num_lessons'])
        self.assertEqual(saved_form.lesson_duration_hours, self.form_input['lesson_duration_hours'])
