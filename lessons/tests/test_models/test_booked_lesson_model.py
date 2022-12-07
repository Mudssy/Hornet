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
        self.request = LessonRequest.objects.create(
            days_available="4",
            num_lessons= 4,
            lesson_gap_weeks=LessonRequest.LessonGap.WEEKLY,
            lesson_duration_hours=1,
            requestor=self.student,
            extra_requests='I want to practice music theory with Mrs Doe at least once, and practice the clarinet at least twice',
            teacher=self.teacher
        )
        self.booked_lesson = BookedLesson.objects.create(
            start_time = datetime.datetime.now(),
            duration = self.request.lesson_duration_hours,
            teacher = self.teacher,
            student = self.student
        )

    def test_booked_lesson_saved(self):
        lesson_count = BookedLesson.objects.filter(student=self.student).count()
        self.assertEqual(lesson_count, 1)