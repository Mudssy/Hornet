"""Test of the request view"""
from django.test import TestCase
from django.urls import reverse
from lessons.forms import MakeRequestForm
from ..models import Student, Request

class RequestViewTestCase(TestCase):

    def setUp(self):
        self.url = reverse('make_request')
        self.form_input = {
            'availability': 'Sometime',
            'num_lessons': 2,
            'lesson_gap': 4,
            'duration': 45,
            'extra_requests': 'Mr Goodteacher please'
        }

    def test_valid_request_form(self):
        form = MakeRequestForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    
