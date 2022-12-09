from django.test import TestCase
from django.urls import reverse
from lessons.models import User
from django import forms

class TestEditAdminViewTestCase(TestCase):
    fixtures = [
        'lessons/tests/fixtures/other_users.json'
    ]

    def setUp(self):
        self.admin = User.objects.get(username="@administrator")
        self.director = User.objects.get(username="@director")
        self.url = reverse('edit_account', kwargs={'user_id': self.admin.id})
        self.form_input = {
            'first_name':self.admin.first_name,
            'last_name':self.admin.last_name,
            'email':self.admin.email,
            'username':self.admin.username,
            'new_password':"Password123",
            'confirm_password':"Password123",
            'account_type': 3,
            'user_id':self.admin.id
        }

    def test_edit_admin_url(self):
        self.assertEqual(self.url, '/edit_account/4')

    def test_edit_admin_uses_correct_template(self):
        self.client.login(username=self.director.username, password="Password123")
        response = self.client.get(self.url, {'user_id':self.admin.id})
        self.assertTemplateUsed(response, 'edit_account.html')

    def test_non_director_cannot_edit_admin(self):
        self.client.login(username=self.admin.username, password='Password123')
        response = self.client.get(self.url)
        redirect_url = reverse('feed')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

    def test_edit_does_not_create_new_admins(self):
        user_count_before = User.objects.count()
        self.client.login(username=self.director.username, password="Password123")
        self.client.post(self.url, self.form_input)
        user_count_after = User.objects.count()
        self.assertEqual(user_count_before, user_count_after)

    def test_admin_edit_saves_correctly(self):
        self.form_input['first_name'] = "differentname"
        self.client.login(username=self.director.username, password="Password123")
        before_admin_name = self.admin.first_name
        self.client.post(self.url, self.form_input)
        changed_admin = User.objects.get(username=self.form_input['username'])
        self.assertNotEqual(changed_admin.first_name, before_admin_name)
        self.assertEqual(changed_admin.first_name, self.form_input['first_name'])

    def test_admin_password_saves(self):   ## test fails even tho it shouldnt 
        new_p = "NewPassword123"
        new_p_hash = 'pbkdf2_sha256$390000$3esLiMGTz4anKPFzChww4R$3KpwFBj/Qn12sqgcTod8lNYtTnX9mGxjhiQrCB/JV7E='
        self.form_input['new_password'] = new_p
        self.form_input['confirm_password'] = new_p
        self.client.login(username=self.director.username, password="Password123")
        self.client.post(self.url, self.form_input)
        update_admin = User.objects.get(id=self.admin.id)
        self.assertEqual(update_admin.password, new_p_hash)

    def test_admin_edit_redirects_after_save(self):
        self.client.login(username=self.director.username, password="Password123")
        response = self.client.post(self.url, self.form_input, follow=True)
        redirect_url = reverse('user_list', kwargs={"account_type": self.form_input["account_type"]})
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
