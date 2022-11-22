from django.contrib.auth.hashers import check_password
from django import forms
from django.urls import reverse
from django.test import TestCase
from lessons.forms import SignUpForm, RequestLessonsForm
from lessons.models import User, LessonRequest, Invoice


class RequestFormTestCase(TestCase):
    

    fixtures = [
        'lessons/tests/fixtures/default_student_user.json',
        'lessons/tests/fixtures/other_users.json'
    ]


    def setUp(self):
        self.admin = User.objects.get(username="@administrator")
        self.student = User.objects.get(username="@johndoe")
        self.url = reverse('invoices')
        student_invoice_id = Invoice.objects.filter(associated_student=self.student).count()+1
        self.invoice_id = str(self.student.id).rjust(4, '0') + "-" + (str(student_invoice_id)).rjust(4, '0')

        self.invoice = Invoice.objects.create(
            associated_student=self.student,
            number_of_lessons=1,
            lesson_duration=1,
            hourly_cost=40,
            total_price=40*1*1,
            invoice_id = self.invoice_id
        )   

    def test_invoice_view_contains_invoice_id(self):
        self.client.login(username=self.student.username, password="Password123")
        response = self.client.get(self.url)
        self.assertContains(response, self.invoice_id)

    def test_multiple_invoices_all_show(self):
        id_list = []
        self.client.login(username=self.student.username, password="Password123")


        for i in range(10):
            student_invoice_id = Invoice.objects.filter(associated_student=self.student).count()+1
            self.invoice_id = str(self.student.id).rjust(4, '0') + "-" + (str(student_invoice_id)).rjust(4, '0')

            self.invoice = Invoice.objects.create(
                associated_student=self.student,
                number_of_lessons=1,
                lesson_duration=1,
                hourly_cost=40,
                total_price=40*1*1,
                invoice_id = self.invoice_id
            )
            id_list.append(self.invoice_id)

        response = self.client.get(self.url)
        for id in id_list:
            self.assertContains(response, id)

        