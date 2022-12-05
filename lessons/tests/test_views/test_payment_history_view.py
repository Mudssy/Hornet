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
        self.teacher = User.objects.get(username="@teacher")
        self.url = reverse('payment_history')
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
            'submit': 'Approve'
        }
        self.client.login(username=self.student.username, password="Password123")
        student_invoice_id = Invoice.objects.filter(associated_student=self.student).count()+1
        self.invoice_id = str(self.student.id).rjust(4, '0') + "-" + (str(student_invoice_id)).rjust(4, '0')

    def test_payment_history_created(self):
        # the setup should run code that generates some payment history and log in

        #checks that having one approved request
        response = self.client.get(self.url)
        self.assertContains(response, "Current Credit")
        payment_count = len(response.context['payments'])

        #the empty string
        self.assertEqual(payment_count, 1)

        #approve the request
        self.client.login(username=self.admin.username, password="Password123")
        self.client.post(reverse('edit_request'), self.form_input)
        payment = response.context['payments']

        # now the string with some history
        self.assertEqual(len(payment), 1)
        payment_string = "".join(payment)
        self.assertIn(payment_string, 'Invoice id')


        self.assertIn(payment_string, self.invoice_id)