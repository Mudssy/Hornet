from django import forms
from django.test import TestCase
from lessons.forms import SubmitPaymentForm
from lessons.models import User, Invoice


def SubmitPaymentTestCase(TestCase):
    fixtures = [
        'lessons/tests/fixtures/default_student_user.json',
        'lessons/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.url = '/submit_payments/'
        self.admin = User.objects.get(username="@director", password="Password123")
        self.invoice = Invoice.objects.create(
            associated_student=self.student,
            number_of_lessons=1,
            lesson_duration=1,
            hourly_cost=40,
            total_price=40*1*1,
            invoice_id = self.invoice_id
        )