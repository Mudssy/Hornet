from django.test import TestCase
from django.urls import reverse
from lessons.models import User

class TestDeleteUserViewTestCase(TestCase):
    fixtures = [
        'lessons/tests/fixtures/other_users.json',
        'lessons/tests/fixtures/default_student_user.json'
    ]

    def setUp(self):
        self.admin = User.objects.get(username="@administrator")
        self.director = User.objects.get(username="@director")
        self.student= User.objects.get(username="@johndoe")
        self.teacher = User.objects.get(username="@teacher")
        self.url = reverse('delete_user', kwargs={'user_id': self.student.id})

    def test_users_canot_delete_other_users(self):
        before_count = User.objects.count()
        self.client.login(username=self.student.username, password="Password123")
        other_user = User.objects.get(username="@janedoe")
        delete_url = reverse('delete_user', kwargs={'user_id': other_user.id})
        response = self.client.post(delete_url)
        redirect_url = reverse('feed')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        after_count = User.objects.count()
        self.assertEqual(before_count, after_count)

    def test_teachers_cannot_delete_users(self):
        # same as above test but login as a teacher instead
        before_count = User.objects.count()
        self.client.login(username=self.teacher.username, password="Password123")
        other_user = User.objects.get(username="@janedoe")
        delete_url = reverse('delete_user', kwargs={'user_id': other_user.id})
        response = self.client.post(delete_url)
        redirect_url = reverse('feed')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        after_count = User.objects.count()
        self.assertEqual(before_count, after_count)

    def test_users_are_removed_from_database(self):
        self.client.login(username=self.director.username, password="Password123")
        user_count_before = User.objects.count()
        self.client.post(self.url)
        user_count_after = User.objects.count()
        self.assertEqual(user_count_after, user_count_before-1)

    def test_redirects_after_delete(self):
        self.client.login(username=self.director.username, password="Password123")
        response = self.client.post(self.url, {'user_id':self.admin.id})
        redirect_url = reverse('user_list', kwargs={"account_type": self.student.account_type})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
