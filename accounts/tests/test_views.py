from django.contrib.auth import get_user_model, REDIRECT_FIELD_NAME
from django.test import TestCase

from shorturls.models import Url


class AccountsViewsTestCase(TestCase):
    def setUp(self):
        self.user_data = {
            'username': 'user',
            'email': 'email@email.loc',
            'password': 'password'
        }
        self.user = get_user_model().objects.create_user(**self.user_data)

        username_field = self.user.USERNAME_FIELD
        post = {
            'username': self.user_data.get(username_field),
            'password': self.user_data.get('password')
        }
        self.client.login(**post)

        self.url_data = {
            'url': 'hello.loc',
            'description': 'new description',
            'account': self.user
        }
        self.url = Url.objects.create(**self.url_data)

    def test_accounts_views__profile(self):
        response = self.client.get('/accounts/profile/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'accounts/profile.html')

    def test_accounts_views__change_password__valid(self):
        post = {
            'old_password': self.user_data.get('password'),
            'new_password1': 'newpassword',
            'new_password2': 'newpassword'
        }
        response = self.client.post('/accounts/change_password/', post)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/change_password/done/')

    def test_accounts_views__change_password__not_valid(self):
        post = {
            'old_password': self.user_data.get('password'),
            'new_password1': 'newpassword1',
            'new_password2': 'newpassword2'
        }
        response = self.client.post('/accounts/change_password/', post)
        self.assertEqual(response.status_code, 400)

    def test_accounts_views__change_password_done(self):
        response = self.client.get('/accounts/change_password/done/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'accounts/change_password_done.html')

    def test_accounts_views__urls(self):
        response = self.client.get('/accounts/urls/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'accounts/urls.html')

    def test_accounts_views_urls_add(self):
        response = self.client.get('/accounts/urls/add/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'accounts/urls_add.html')

    def test_accounts_views__urls_add__valid(self):
        post = {
            'url': 'test.loc',
            'description': ''
        }
        response = self.client.post('/accounts/urls/add/', post)
        self.assertEqual(response.status_code, 302)
        url = Url.objects.last()
        self.assertRedirects(response, '/accounts/urls/%s/detail/' % url.id)

    def test_accounts_views__urls_add__not_valid(self):
        post = {
            'url': 'notvalid',
            'description': ''
        }
        response = self.client.post('/accounts/urls/add/', post)
        self.assertEqual(response.status_code, 400)

    def test_accounts_views__urls_detail(self):
        response = self.client.get('/accounts/urls/%s/detail/' % self.url.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'accounts/urls_detail.html')

    def test_accounts_views__urls_change(self):
        response = self.client.get('/accounts/urls/%s/change/' % self.url.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'accounts/urls_change.html')

    def test_accounts_views__urls_change__valid(self):
        post = {
            'description': 'new description',
            'is_active': False
        }
        response = self.client.post('/accounts/urls/%s/change/' % self.url.id, post)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/urls/%s/detail/' % self.url.id)

    def test_accounts_views__urls_change__not_valid(self):
        post = {}
        response = self.client.post('/accounts/urls/%s/change/' % self.url.id, post)
        self.assertEqual(response.status_code, 400)


class AccountsViewsAnonymousUserTestCase(TestCase):
    def redirect_anonymous_user(self, path):
        response = self.client.get(path)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/auth/login/?%s=%s' % (REDIRECT_FIELD_NAME, path))

    def test_accounts_views__anonymous_user(self):
        self.redirect_anonymous_user('/accounts/profile/')
        self.redirect_anonymous_user('/accounts/change_password/')
        self.redirect_anonymous_user('/accounts/change_password/done/')
        self.redirect_anonymous_user('/accounts/urls/')
        self.redirect_anonymous_user('/accounts/urls/add/')
        self.redirect_anonymous_user('/accounts/urls/1/detail/')
        self.redirect_anonymous_user('/accounts/urls/1/change/')
