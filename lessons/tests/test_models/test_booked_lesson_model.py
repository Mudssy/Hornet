from django.core.exceptions import ValidationError
from django.test import TestCase
from lessons.models import User, LessonRequest, BookedLesson
import datetime

class BookedLessonModelTestCase(TestCase):
    """Unit tests for the booked lesson model"""

    fixtures = [
        'lessons/tests/fixtures/default_student_user.json',
        'lessons/tests/fixtures/other_users.json'
    ]
    def setUp(self):
        self.student = User.objects.get(username="@johndoe")
        self.teacher = User.objects.get(username="@teacher")
        self.request = LessonRequest.objects.get(requestor=self.student)
        self.booked_lesson = BookedLesson.objects.get(id=99)

    def test_booked_lesson_saved(self):
        lesson_count = BookedLesson.objects.filter(student=self.student).count()
        self.assertEqual(lesson_count, 1)