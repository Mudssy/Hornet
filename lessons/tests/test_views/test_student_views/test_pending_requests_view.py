from django.test import TestCase
from django.urls import reverse
from lessons.models import LessonRequest, User

class PendingRequestTest(TestCase):

    fixtures = [
        'lessons/tests/fixtures/default_student_user.json',
        'lessons/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.student = User.objects.get(username='@johndoe')
        self.url = reverse('pending_requests')
        self.request = LessonRequest.objects.get(requestor=self.student)

    # def test_delete_button_deletes_request(self):
    #     self.client.login(username=self.student.username, password="Password123")
    #     before = LessonRequest.objects.count()
    #     response = self.client.post('/delete_request/', {'id':self.request.id}, follow=True)
    #     after = LessonRequest.objects.count()
    #     self.assertEqual(before - 1, after)
    #     redirect_url = reverse('pending_requests')
    #     self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)