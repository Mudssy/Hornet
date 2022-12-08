from django.contrib.auth.hashers import check_password
from django import forms
from django.urls import reverse
from django.test import TestCase
from lessons.forms import SignUpForm, RequestLessonsForm
from lessons.models import User, LessonRequest, Invoice
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
        self.request = LessonRequest.objects.get(requestor=self.student)
        with open('lessons/tests/fixtures/lesson_request_form_input.json', 'r') as file:
            self.form_input=json.load(file)
            self.form_input['teacher'] = str(self.teacher.id)
        self.url = reverse('edit_request',  kwargs={'request_id': self.request.id})

    def test_approved_request_generates_invoice(self):
        before=Invoice.objects.count()
        self.client.login(username=self.admin.username, password="Password123")
        self.client.post(self.url, self.form_input)
        after=Invoice.objects.count()
        self.assertEqual(before + 1, after)

    def test_invoice_has_correct_id(self):
        self.client.login(username=self.admin.username, password="Password123")
        self.client.post(self.url, self.form_input)
        invoice = Invoice.objects.filter(associated_student=self.student).get()
        student_invoice_id = Invoice.objects.filter(associated_student=self.student).count()
        self.assertEqual(str(self.student.id).rjust(4, '0') + "-" + (str(student_invoice_id)).rjust(4, '0'), invoice.invoice_id)
