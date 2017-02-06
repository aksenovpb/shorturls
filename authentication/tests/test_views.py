from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from authentication.tokens import user_is_active_token_generator


class AuthenticationViewTestCase(TestCase):
    def setUp(self):
        self.user_data = {
            'username': 'user_duplicate',
            'email': 'user@duplicate.loc',
            'password': 'userDuplicate'
        }
        self.user = get_user_model().objects.create_user(**self.user_data)

    def test_authentication_views__signup(self):
        response = self.client.get('/auth/signup/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'authentication/registration.html')
        self.assertEqual(response.context['title'], 'Registration')

    def test_authentication_views__signup__valid(self):
        post = {
            'username': 'user',
            'email': 'email@email.loc',
            'password1': 'userPassword1',
            'password2': 'userPassword1'
        }
        response = self.client.post('/auth/signup/', post)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')
        user = get_user_model().objects.last()
        self.assertEqual(user.username, post.get('username'))
        self.assertEqual(user.email, post.get('email'))
        self.assertTrue(user.check_password(post.get('password1')))

    def test_authentication_views__signup__valid_duplicate(self):
        post = {
            'username': self.user_data.get('username'),
            'email': self.user_data.get('email'),
            'password1': self.user_data.get('password'),
            'password2': self.user_data.get('password')
        }
        response = self.client.post('/auth/signup/', post)
        self.assertEqual(response.status_code, 400)

    def test_authentication_views__singup__not_valid(self):
        post = {
            'username': 'not_valid'*10,
            'email': 'not_valid',
            'password1': 'userPassword1',
            'password2': ''
        }
        response = self.client.post('/auth/signup/', post)
        self.assertEqual(response.status_code, 400)

    def test_authentication_views__login(self):
        response = self.client.get('/auth/login/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'authentication/login.html')
        self.assertEqual(response.context['title'], 'Login')

    def test_authentication_views__login__valid(self):
        username_field = get_user_model().USERNAME_FIELD
        post = {
            'username': self.user_data.get(username_field),
            'password': self.user_data.get('password')
        }
        response = self.client.post('/auth/login/', post)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/auth/login/')
        self.assertTrue(self.client.login(**post))

    def test_authentication_views__login__not_valid(self):
        post = {
            'username': 'username'*10,
            'password': 'not valid'
        }
        response = self.client.post('/auth/login/', post)
        self.assertEqual(response.status_code, 400)
        self.assertFalse(self.client.login(**post))

    def test_authentication_views__logout(self):
        response = self.client.get('/auth/logout/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'authentication/logout.html')
        self.assertEqual(response.context['title'], 'Logged out')

    def test_authentication_views__activate__valid(self):
        self.user.is_activate = False
        self.user.save()
        params = {
            'uid': urlsafe_base64_encode(force_bytes(self.user.pk)),
            'token': user_is_active_token_generator.make_token(self.user)
        }
        response = self.client.get('/auth/activate/%s/%s/' % (params['uid'], params['token']))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['validlink'])

    def test_authentication_views__activate__not_valid(self):
        params = {
            'uid': urlsafe_base64_encode(force_bytes(0)),
            'token': user_is_active_token_generator.make_token(self.user)
        }
        response = self.client.get('/auth/activate/%s/%s/' % (params['uid'], params['token']))
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.context['validlink'])
