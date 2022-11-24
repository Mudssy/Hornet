from django.core.exceptions import ValidationError
from django.test import TestCase
from lessons.models import User, LessonRequest

class RequestModelTestCase(TestCase):
    """Unit tests for the request model"""

    fixtures = [
        'lessons/tests/fixtures/default_student_user.json',
        'lessons/tests/fixtures/other_users.json'
    ]
    def setUp(self):
        self.student = User.objects.get(username="@johndoe")
        self.request = LessonRequest.objects.create(
            days_available="4",
            num_lessons=4,
            lesson_gap_weeks=LessonRequest.LessonGap.WEEKLY,
            lesson_duration_hours=1,
            requestor=self.student,
            extra_requests='I want to practice music theory with Mrs Doe at least once, and practice the clarinet at least twice'
        )

    def test_student_can_have_multiple_requests(self):
        second_request = LessonRequest.objects.create(
            days_available="2",
            num_lessons=4,
            lesson_gap_weeks=LessonRequest.LessonGap.FORTNIGHTLY,
            lesson_duration_hours=1,
            requestor=self.student,
            extra_requests='I like music'
        )
        self._assert_request_is_valid()
        self.request=second_request
        self._assert_request_is_valid()

    def test_requestor_cannot_be_blank(self):
        self.request.requestor = None
        self._assert_request_is_invalid()

    def test_days_available_cannot_be_blank(self):
        self.request.days_available = None
        self._assert_request_is_invalid()

    def test_num_lessons_cannot_be_blank(self):
        self.request.num_lessons = None
        self._assert_request_is_invalid()

    def test_lesson_gap_weeks_cannot_be_blank(self):
        self.request.lesson_gap_weeks = None
        self._assert_request_is_invalid()

    def test_lesson_duration_hours_cannot_be_blank(self):
        self.request.lesson_duration_hours = None
        self._assert_request_is_invalid()

    def test_extra_requests_can_be_blank(self):
        self.request.extra_requests = None
        self._assert_request_is_valid()

    def _assert_request_is_valid(self):
        try:
            self.request.full_clean()
        except(ValidationError):
            self.fail('Test should be valid')

    def _assert_request_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.request.full_clean()
