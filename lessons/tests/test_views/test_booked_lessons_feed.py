from django.contrib.auth.hashers import check_password
from django import forms
from django.urls import reverse
from django.test import TestCase
from lessons.forms import SignUpForm, RequestLessonsForm
from lessons.models import User, LessonRequest

class BookedLesson(TestCase):
    """Tests of the feed view."""

    fixtures=[
        'lessons/tests/fixtures/default_student_user.json',
        'lessons/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.student = User.objects.get(username="@johndoe")
        self.admin = User.objects.get(username="@administrator")
        self.form_input = {
            'days_available' : '2',
            'num_lessons' : 4,
            'lesson_gap_weeks' : LessonRequest.LessonGap.WEEKLY,
            'lesson_duration_hours' : 1,
            'requestor' : self.user,
            'extra_requests' : 'I want to practice music theory with Mrs Doe at least once, and practice the clarinet at least twice'
        }
        self.url = reverse('booked_lessons')
        

    def admin_approved_test_appears_in_student_feed(self):
        self.client.login(username=self.student.username, password="Password123")
        self.client.post(reverse('lesson_requests'), self.form_input)
        request = LessonRequest.objects.get(requestor=self.student)
        response = self.client.get(self.url)
        self.assertNotContains(response, request)
        response = self.client.get(reverse('pending_requests'))
        self.assertContains(response, request)
        self.client.login(username=self.admin.username, password="Password123")
        self.form_input['request_id'] = request.id
        self.client.post(self.url, self.form_input)
        response = self.client.get(self.url)
        self.assertContains(response, request)

