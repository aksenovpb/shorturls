from django.test import TestCase
from django.core.urlresolvers import reverse


class AuthenticationUrlsTestCase(TestCase):

    def test_authentication_urls__signup(self):
        self.assertEqual(reverse('authentication:signup'), '/auth/signup/')

    def test_authentication_urls__login(self):
        self.assertEqual(reverse('authentication:login'), '/auth/login/')

    def test_authentication_urls__logout(self):
        self.assertEqual(reverse('authentication:logout'), '/auth/logout/')

    def test_authentication_urls__activate(self):
        args = ('uidb64', 'tokenpart1-tokenpart2')
        self.assertEqual(reverse('authentication:activate', args=args), '/auth/activate/uidb64/tokenpart1-tokenpart2/')

    def test_authentication_urls__password_reset(self):
        self.assertEqual(reverse('authentication:password_reset'), '/auth/password_reset/')

    def test_authentication_urls__password_reset_done(self):
        self.assertEqual(reverse('authentication:password_reset_done'), '/auth/password_reset/done/')

    def test_authentication_urls__password_reset_confirm(self):
        args = ('uidb64', 'tokenpart1-tokenpart2')
        self.assertEqual(reverse('authentication:password_reset_confirm', args=args), '/auth/password_reset/confirm/uidb64/tokenpart1-tokenpart2/')

    def test_authentication_urls__password_reset_complete(self):
        self.assertEqual(reverse('authentication:password_reset_complete'), '/auth/password_reset/complete/')