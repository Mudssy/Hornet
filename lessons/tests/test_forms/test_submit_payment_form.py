from django.contrib.auth.hashers import check_password
from django import forms
from django.urls import reverse
from django.test import TestCase
from lessons.forms import SignUpForm, RequestLessonsForm
from lessons.models import User, LessonRequest, Invoice
from lessons import helpers

class PaymentFormTestCase(TestCase):
    fixtures = [
        'lessons/tests/fixtures/default_student_user.json',
        'lessons/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.url=reverse('submit_payment')
        self.director = User.objects.get(username="@administrator")
        self.student = User.objects.get(username="@johndoe")
        self.teacher = User.objects.get(username="@teacher")

        self.lesson_request = LessonRequest.objects.get(requestor=self.student)
        self.form_input = {
            'requestor': self.student,
            'days_available': ['1', '2'],
            'lesson_gap_weeks': LessonRequest.LessonGap.WEEKLY,
            'num_lessons': 2,
            'lesson_duration_hours': 1,
            'extra_requests': 'magic piano skills',
            'submit': 'Submit',
            'teacher': str(self.teacher.id)
        }

        print(self.lesson_request)
        self.lesson_price = 1 * 1 * 40
        self.url = reverse('submit_payment')
        
        self.lesson_request.is_booked = True
        self.invoice = helpers.create_invoice(self.lesson_request)
        self.invoice_id = self.invoice.invoice_id

        self.payment_info = {
            'amount_paid': 20,
            'id': self.invoice_id
        }
    
    def test_approved_request_generates_inovice_in_director_feed(self):
        # sets up our invoice object
        self.client.login(username=self.director.username, password="Password123")
        self.client.post(reverse('edit_request',  kwargs={'request_id': self.lesson_request.id}), self.form_input)
        approved_request = LessonRequest.objects.get(id=self.lesson_request.id)
        self.assertIsInstance(approved_request, LessonRequest)
        self.assertTrue(approved_request.is_booked)
        request_id = approved_request.id
        self.assertEqual(self.lesson_price, self.invoice.amount_outstanding)

        # checks director feed
        response = self.client.get(self.url)
        self.assertContains(response, self.invoice.id)
        
        
    def test_paid_invoice_disappears(self):
        self.payment_info['amount_paid'] = self.lesson_price
        self.client.post(self.url, self.payment_info)
        response = self.client.get(self.url)
        this_invoice = Invoice.objects.get(invoice_id=self.invoice_id)
        self.assertNotContains(response, self.invoice_id)

    def test_half_paid_invoice_appears(self):
        partial_payment = 20
        self.payment_info['amount_paid'] = partial_payment
        self.client.post(self.url, self.payment_info)
        response = self.client.get(self.url)
        this_invoice = Invoice.objects.get(invoice_id=self.invoice_id)
        self.assertContains(response, self.invoice_id)
        self.assertEqual(self.lesson_price - partial_payment, this_invoice.amount_outstanding)

    def test_cannot_pay_over_cost(self):
        overpayment = 100
        self.payment_info['amount_paid'] = overpayment
        self.client.post(self.url, self.payment_info)
        this_invoice = Invoice.objects.get(invoice_id=self.invoice_id)
        self.assertFalse(this_invoice.is_paid)
        self.assertEqual(this_invoice.amount_paid, 0)
        self.assertEqual(this_invoice.amount_outstanding, self.lesson_price)
        