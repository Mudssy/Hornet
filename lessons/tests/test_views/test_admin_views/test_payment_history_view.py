from django.contrib.auth.hashers import check_password
from django import forms
from django.urls import reverse
from django.test import TestCase
from lessons.forms import SignUpForm, RequestLessonsForm
from lessons.models import User, LessonRequest, Invoice, BookedLesson
import json

class RequestFormTestCase(TestCase):
    

    fixtures = [
        'lessons/tests/fixtures/default_student_user.json',
        'lessons/tests/fixtures/other_users.json'
    ]


    def setUp(self):
        self.admin = User.objects.get(username="@administrator")
        self.student = User.objects.get(username="@johndoe")
        self.teacher = User.objects.get(username="@teacher")
        self.url = reverse('payment_history')
        self.request = LessonRequest.objects.get(requestor=self.student)
        with open('lessons/tests/fixtures/lesson_request_form_input.json', 'r') as file:
            self.form_input=json.load(file)
            self.form_input['teacher'] = str(self.teacher.id)

        self.client.login(username=self.student.username, password="Password123")
        student_invoice_id = Invoice.objects.filter(associated_student=self.student).count()+1
        self.invoice_id = str(self.student.id).rjust(4, '0') + "-" + (str(student_invoice_id)).rjust(4, '0')

    def test_payment_history_created(self):
        # checks that having one approved request
        response = self.client.get(self.url)
        self.assertContains(response, "Current Credit")
        payment_count = len(response.context['payments'])

        self.assertEqual(payment_count, 0)

        #approve the request
        self.client.login(username=self.admin.username, password="Password123")
        self.client.post(reverse('edit_request', kwargs={'request_id': self.request.id}), self.form_input)
        self.student = User.objects.get(username="@johndoe")
        payment_string = self.student.payment_history_csv


        self.assertIn(self.invoice_id, payment_string)

