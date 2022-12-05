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
        self.teacher = User.objects.get(username="@teacher")
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
            'id':self.request.id,
            'edit': 'Edit'
        }

    def test_edit_request_url(self):
        self.assertEqual(self.url, "/edit_request/")

    def test_edit_request_uses_correct_template(self):
        self.client.login(username=self.admin.username, password="Password123")
        response = self.client.get(self.url, {'id':self.request.id})
        self.assertTemplateUsed(response, 'edit_request.html')
    
    def test_edit_does_not_create_or_approve_requests(self):
        before_approved_request = LessonRequest.objects.filter(is_booked=False).count()
        request_count = LessonRequest.objects.count()
        self.client.login(username=self.admin.username, password="Password123")
        self.client.post(self.url, self.form_input)
        after_count = LessonRequest.objects.count()
        self.assertEqual(request_count, after_count)
        approved_request = LessonRequest.objects.filter(is_booked=False).count()
        self.assertEqual(before_approved_request, approved_request)

    def test_edit_saves_correctly(self):
        self.form_input['extra_requests'] = "this should change"
        self.client.login(username=self.admin.username, password="Password123")
        self.client.post(self.url, self.form_input)
        approved_request = LessonRequest.objects.filter(id=self.request.id)
        self.assertIn(approved_request[0].extra_requests, "this should change")

    def test_edit_redirects_after_save(self):
        self.client.login(username=self.admin.username, password="Password123")
        response = self.client.post(self.url, self.form_input, follow=True)
        redirect_url = reverse('show_all_requests')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_submit_edit_form_approves_request(self):
        self.form_input.pop('edit')
        self.form_input['submit'] = 'Submit'
        not_booked_before = LessonRequest.objects.filter(is_booked=False).count()
        booked_before = LessonRequest.objects.filter(is_booked=True).count()
        request_count = LessonRequest.objects.count()
        self.client.login(username=self.admin.username, password="Password123")
        self.client.post(self.url, self.form_input)
        after_count = LessonRequest.objects.count()
        self.assertEqual(request_count, after_count)

        not_booked_after = LessonRequest.objects.filter(is_booked=False).count()
        booked_after = LessonRequest.objects.filter(is_booked=True).count()
        self.assertEqual(booked_before + 1, booked_after)
        self.assertEqual(not_booked_before, not_booked_after + 1)

    def test_submit_edit_form_edits_request(self):
        self.form_input.pop('edit')
        self.form_input['submit'] = 'Submit'
        self.form_input['extra_requests'] = "this should change"
        self.client.login(username=self.admin.username, password="Password123")
        self.client.post(self.url, self.form_input)
        approved_request = LessonRequest.objects.filter(id=self.request.id)
        self.assertIn(approved_request[0].extra_requests, "this should change")

    def test_student_can_edit(self):
        self.client.login(username=self.student.username, password="Password123")
        response = self.client.get(self.url, {'id': self.request.id})
        self.assertContains(response, 'Edit')

    def test_student_does_not_have_approve_button(self):
        self.client.login(username=self.student.username, password="Password123")
        response = self.client.get(self.url, {'id': self.request.id})
        self.assertContains(response, 'Edit')
        self.assertNotContains(response, 'Approve')

    def test_admin_can_approve_and_edit_request(self):
        self.client.login(username=self.admin.username, password="Password123")
        response = self.client.get(self.url, {'id': self.request.id})
        self.assertContains(response, 'Edit')
        self.assertContains(response, 'Approve')

    def teacher_can_not_access_edit_view(self):
        self.client.login(username=self.teacher.username, password="Password123")
        response = self.client.get(self.url)
        self.assertRedirects(self.url, response, status_code=302, target_status_code=200)