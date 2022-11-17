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
            day_of_week=0,
            num_lessons=4,
            lesson_gap_weeks=LessonRequest.LessonGap.WEEKLY,
            lesson_duration_hours=1,
            requestor=self.student,
            extra_requests='I want to practice music theory with Mrs Doe at least once, and practice the clarinet at least twice'
        )

    def test_student_can_have_multiple_requests(self):
        second_request = LessonRequest.objects.create(
            day_of_week=2,
            num_lessons=4,
            lesson_gap_weeks=LessonRequest.LessonGap.FORTNIGHTLY,
            lesson_duration_hours=1,
            requestor=self.student,
            extra_requests='I like music'
        )
        self._assert_request_is_valid()
        self.request=second_request
        self._assert_request_is_valid()



    def _assert_request_is_valid(self):
        try:
            self.request.full_clean()
        except(ValidationError):
            self.fail('Test should be valid')

    def _assert_request_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.request.full_clean()
