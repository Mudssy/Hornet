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
        self.admin = User.objects.get(username="@administrator")
        self.student = User.objects.get(username="@johndoe")
        self.url = reverse('edit_request')
        self.request = LessonRequest.objects.create(
            requestor=self.student,
            days_available="123",
            lesson_gap_weeks=LessonRequest.LessonGap.WEEKLY,
            num_lessons=2,
            lesson_duration_hours=1,
            extra_requests="testfixture"
        )
        self.form_input = {
            'requestor': self.student,
            'days_available': ['1', '2'],
            'lesson_gap_weeks': LessonRequest.LessonGap.WEEKLY,
            'num_lessons': 2,
            'lesson_duration_hours': 1,
            'extra_requests': 'magic piano skills',
            'request_id':self.request.id
        }

    def test_edit_request_url(self):
        self.assertEqual(self.url, "/edit_request/")

    def test_edit_request_uses_correct_template(self):
        self.client.login(username=self.admin.username, password="Password123")
        response = self.client.get(self.url, {'request_id':self.request.id})
        self.assertTemplateUsed(response, 'edit_request.html')

    def test_student_cannot_edit_requests(self):
        self.client.login(username=self.student.username, password='Password123')
        response = self.client.get(self.url)
        redirect_url = reverse('feed')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
    
    def test_edit_does_not_create_requests(self):
        request_count = LessonRequest.objects.count()
        self.client.login(username=self.admin.username, password="Password123")
        self.client.post(self.url, self.form_input)
        after_count = LessonRequest.objects.count()
        self.assertEqual(request_count, after_count)
        approved_request = LessonRequest.objects.filter(is_booked=True)
        self.assertTrue(approved_request is not None)
        self.assertEqual(approved_request[0].id, self.request.id)

    def test_edit_saves_correctly(self):
        self.form_input['extra_requests'] = "this should change"
        self.client.login(username=self.admin.username, password="Password123")
        self.client.post(self.url, self.form_input)
        approved_request = LessonRequest.objects.filter(is_booked=True)
        self.assertIn(approved_request[0].extra_requests, "this should change")

    def test_edit_redirects_after_save(self):
        self.client.login(username=self.admin.username, password="Password123")
        response = self.client.post(self.url, self.form_input, follow=True)
        redirect_url = reverse('show_all_requests')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)


    