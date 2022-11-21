from django.test import TestCase
from django.urls import reverse
from lessons.models import LessonRequest, User

class MakeRequestTest(TestCase):
    """Tests for the make_request view"""

    fixtures = [
        'lessons/tests/fixtures/default_student_user.json'
    ]

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.url = reverse('make_request')
        self.data = {
            'days_available' : '2',
            'num_lessons' : 4,
            'lesson_gap_weeks' : LessonRequest.LessonGap.WEEKLY,
            'lesson_duration_hours' : 1,
            'requestor' : self.user,
            'extra_requests' : 'I want to practice music theory with Mrs Doe at least once, and practice the clarinet at least twice'
        }

    def test_make_request_url(self):
        self.assertEqual(self.url,'/make_request/')

    def test_successful_new_request(self):
        self.client.login(username=self.user.username, password="Password123")
        request_count_before = LessonRequest.objects.count()
        response = self.client.post(self.url, self.data, follow=True)
        request_count_after = LessonRequest.objects.count()
        self.assertEqual(request_count_after, request_count_before+1)
        newest_request = LessonRequest.objects.latest('request_time')
        self.assertEqual(self.user, newest_request.requestor)
        response_url = reverse('feed')
        self.assertRedirects(
            response, response_url,
            status_code=302, target_status_code=200,
            fetch_redirect_response=True
        )
        self.assertTemplateUsed(response, 'feed.html')
