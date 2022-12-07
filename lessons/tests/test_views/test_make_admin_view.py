from django.test import TestCase
from django.urls import reverse
from lessons.models import User

class MakeAdminViewTest(TestCase):
    fixtures = [
        'lessons/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.director = User.objects.get(username='@director')
        self.url = reverse('make_admin')
        self.form_input = {
            'first_name': 'Tess',
            'last_name': 'Test',
            'email': 'tesstest@example.org',
            'username': '@tesstest',
            'new_password': 'Password123',
            'confirm_password': 'Password123'
        }

    def test_make_admin_url(self):
        self.assertEqual(self.url, '/make_admin/')

    def test_successful_new_admin(self):
        self.client.login(username=self.director.username, password='Password123')
        user_count_before = User.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        user_count_after = User.objects.count()
        self.assertEqual(user_count_after, user_count_before+1)
        new_admin = User.objects.get(username=self.form_input['username'])
        self.assertEqual(new_admin.account_type, 3)
        self.assertTrue(new_admin.is_staff)
        self.assertFalse(new_admin.is_superuser)
        response_url = reverse('feed')
        self.assertRedirects(
            response, response_url,
            status_code=302, target_status_code=200,
            fetch_redirect_response=True
        )
        self.assertTemplateUsed(response, 'feed.html')

    def test_unsuccessful_new_admin(self):
        self.client.login(username=self.director.username, password='Password123')
        user_count_before = User.objects.count()
        self.form_input['confirm_password'] = ""
        response = self.client.post(self.url, self.form_input, follow=True)
        user_count_after = User.objects.count()
        self.assertEqual(user_count_after, user_count_before)
        self.assertTemplateUsed(response, 'make_admin.html')

    def test_admin_cannot_create_new_admin(self):
        self.admin = User.objects.get(username='@administrator')
        self.client.login(username=self.admin.username, password='Password123')
        user_count_before = User.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        user_count_after = User.objects.count()
        self.assertEqual(user_count_after, user_count_before)
