from django.core.exceptions import ValidationError
from django.test import TestCase
from lessons.models import User, LessonRequest, BookedLesson

class BookedLessonModelTestCase(TestCase):
    """Unit tests for the booked lesson model"""

    fixtures = [
        'lessons/tests/fixtures/default_student_user.json',
        'lessons/tests/fixtures/other_users.json'
    ]
    def setUp(self):
        self.student = User.objects.get(username="@johndoe")
        self.request = LessonRequest.objects.create(
            days_available="4",
            num_lessons= 4,
            lesson_gap_weeks=LessonRequest.LessonGap.WEEKLY,
            lesson_duration_hours=1,
            requestor=self.student,
            extra_requests='I want to practice music theory with Mrs Doe at least once, and practice the clarinet at least twice'
        )
        self.booked_lesson = BookedLesson.objects.create(
            associated_lesson_request = self.request,
            num_lessons= 4,
            lesson_gap_weeks=LessonRequest.LessonGap.WEEKLY,
            lesson_duration_hours=1,
            requestor=self.student,
            extra_requests='I want to practice music theory with Mrs Doe at least once, and practice the clarinet at least twice'

        )
        self.staff_member = User.objects.get(username="@petrapickles")

    def test_requestor_cannot_be_blank(self):
        self.booked_lesson.requestor = None
        self._assert_request_is_invalid()

    def test_days_available_cannot_be_blank(self):
        self.booked_lesson.days_available = None
        self._assert_request_is_invalid()

    def test_num_lessons_cannot_be_blank(self):
        self.booked_lesson.num_lessons = None
        self._assert_request_is_invalid()

    def test_lesson_gap_weeks_cannot_be_blank(self):
        self.booked_lesson.lesson_gap_weeks = None
        self._assert_request_is_invalid()

    def test_lesson_duration_hours_cannot_be_blank(self):
        self.booked_lesson.lesson_duration_hours = None
        self._assert_request_is_invalid()

    def test_extra_requests_can_be_blank(self):
        self.booked_lesson.extra_requests = None
        self._assert_request_is_valid()

    def _assert_request_is_valid(self):
        try:
            self.booked_lesson.full_clean()
        except(ValidationError):
            self.fail('Test should be valid')

    def _assert_request_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.booked_lesson.full_clean()
