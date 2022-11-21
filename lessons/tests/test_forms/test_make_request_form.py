from django.contrib.auth.hashers import check_password
from django import forms
from django.urls import reverse
from django.test import TestCase
from lessons.forms import SignUpForm, RequestLessonsForm
from lessons.models import User, LessonRequest


class RequestFormTestCase(TestCase):
    fixtures = [
        'lessons/tests/fixtures/default_student_user.json',
        'lessons/tests/fixtures/other_users.json'
    ]


    def setUp(self):
        self.url=reverse('make_request')
        self.student = User.objects.get(username="@johndoe")
        self.form_input = {
            'requestor': self.student,
            'days_available': ['1', '2'],
            'lesson_gap_weeks': LessonRequest.LessonGap.WEEKLY,
            'num_lessons': 2,
            'lesson_duration_hours': 1,
            'extra_requests': 'magic piano skills'
        }

    def test_valid_form_is_valid(self):
        self.form = RequestLessonsForm(data=self.form_input)
        self.assertTrue(self.form.is_valid())

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
        saved_form = LessonRequest.objects.get(requestor=self.student)
        self.assertEqual(saved_form.requestor, self.student)
        self.assertEqual(saved_form.days_available, '12')
        self.assertEqual(saved_form.lesson_gap_weeks, 2)
        self.assertEqual(saved_form.num_lessons, self.form_input['num_lessons'])
        self.assertEqual(saved_form.lesson_duration_hours, self.form_input['lesson_duration_hours'])
