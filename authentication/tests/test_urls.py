from django.test import TestCase
from django.core.urlresolvers import reverse


class AuthenticationUrlsTestCase(TestCase):

    def test_authentication_urls__signup(self):
        self.assertEqual(reverse('authentication:signup'), '/auth/signup/')

    def test_authentication_urls__login(self):
        self.assertEqual(reverse('authentication:login'), '/auth/login/')

    def test_authentication_urls__logout(self):
        self.assertEqual(reverse('authentication:logout'), '/auth/logout/')
