from django.test import TestCase
from django.urls import reverse
from lessons.models import LessonRequest, User, Invoice
from lessons.helpers import create_invoice, update_invoice
from lessons.forms import SignUpForm, RequestLessonsForm

class MakeRequestTest(TestCase):
    """Tests for the make_request view"""

    fixtures = [
        'lessons/tests/fixtures/default_student_user.json',
        'lessons/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.student = User.objects.get(username="@johndoe")
        self.admin = User.objects.get(username="@administrator")

        self.request = LessonRequest.objects.create(
            days_available=0,
            num_lessons=4,
            lesson_gap_weeks=LessonRequest.LessonGap.WEEKLY,
            lesson_duration_hours=1,
            requestor=self.student,
            extra_requests='I want to practice music theory with Mrs Doe at least once, and practice the clarinet at least twice'
        )

        self.lesson_price = self.request.num_lessons * self.request.lesson_duration_hours * 40
        


    def test_create_invoice_creates_invoice(self):
        before = Invoice.objects.count()
        self.assertEqual(self.student.balance, 0)
        self.request.is_booked=True
        create_invoice(self.request)
        self.assertEqual(self.student.balance, -self.lesson_price)
        after = Invoice.objects.count()
        self.assertEqual(before + 1, after)




    def test_make_and_update_payment_update_objects_correctly(self):
        self.assertEqual(self.student.balance, 0)
        before = Invoice.objects.count()
        self.client.login(username=self.admin.username, password="Password123")
        
        # approve the request
        self.request.is_booked=True
        invoice = create_invoice(self.request)
        after = Invoice.objects.count()
        self.assertEqual(before + 1, after)

        # check invoice is generated correctly
        invoice_count = Invoice.objects.count()
        self.assertEqual(invoice_count, before + 1)
        self.assertEqual(invoice.amount_paid, 0)

        # send a payment
        invoice = update_invoice(invoice, 10)
        invoice_count = Invoice.objects.count()
        self.assertEqual(invoice_count, before + 1)
        self.assertEqual(invoice.amount_paid, 10)
        self.assertFalse(invoice.is_paid)

        # send the rest of the payment
        outstanding = invoice.amount_outstanding
        invoice = update_invoice(invoice, outstanding)
        self.assertEqual(invoice.amount_paid, outstanding + 10)
        self.assertTrue(invoice.is_paid)


    def test_update_payment_rejects_overpayment(self):
        self.request.is_booked = True
        invoice = create_invoice(self.request)
        before = Invoice.objects.count()

        self.assertRaises(ValueError, update_invoice, invoice, invoice.amount_outstanding + 1)
        after = Invoice.objects.count()
        self.assertEqual(before, after)
        

