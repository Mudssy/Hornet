from django.contrib.auth.hashers import check_password
from django import forms
from django.urls import reverse
from django.test import TestCase
from lessons.forms import SignUpForm, RequestLessonsForm
from lessons.models import User, LessonRequest, Invoice
from lessons.helpers import create_invoice

class PaymentHistoryFormTestCase(TestCase):
    

    fixtures = [
        'lessons/tests/fixtures/default_student_user.json',
        'lessons/tests/fixtures/other_users.json'
    ]


    def setUp(self):
        self.student = User.objects.get(username="@johndoe")
        self.teacher = User.objects.get(username="@teacher")
        self.admin = User.objects.get(username="@administrator")
        self.director = User.objects.get(username="@director")
        self.url = reverse('user_payment_history', kwargs={'user_id':self.student.id})
        self.request = LessonRequest.objects.get(requestor=self.student)
        # this should create the relevant payment history
        self.request.is_booked=True
        self.invoice = create_invoice(self.request)

    
    def test_user_payment_history_url(self):
        response = self.client.get(self.url, {'user_id': self.student.id})

        # this is as part of the invoice id
        self.assertContains(response, self.student.balance)

    def test_user_payment_history_updates(self):
        response = self.client.get(self.url, {'user_id': self.student.id})

        # this is as part of the invoice id
        self.assertContains(response, self.student.id)
        pay_list = response.context.get('payments')
        before_payment = len(pay_list)

        # submit a payment
        self.client.post(reverse('submit_payment'), {'id': self.invoice.invoice_id, 'amount_paid': 20})
        response = self.client.get(self.url, {'user_id': self.student.id})
        self.assertContains(response, '20')
        pay_list = response.context.get('payments')
        after_payment = len(pay_list)

        # check this payment renders in history view
        self.assertEqual(before_payment + 1, after_payment)