from django.contrib.auth import get_user_model
from django.test import TestCase
from django.core.urlresolvers import reverse
from shorturls.views import index
from shorturls.models import Url, Referrer, Logging


class ShotrurlsViewsTestCase(TestCase):
    def setUp(self):
        self.url_str = 'ya.ru'
        self.url, created = Url.objects.get_or_create(url=self.url_str)
        self.user_data = {
            'username': 'user',
            'email': 'email@email.loc',
            'password': 'userPassword1',
        }
        self.user = get_user_model().objects.create_user(**self.user_data)

    def test_shorturls_views__index(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_shorturls_views__index_url_valid(self):
        data = {'url': 'http://yatest.ru'}
        response = self.client.post('/', data)
        self.assertEqual(response.status_code, 201)

    def test_shorturls_views__index_url_valid_user_is_authenticate(self):
        username_field = get_user_model().USERNAME_FIELD
        user_data = {
            'username': self.user_data.get(username_field),
            'password': self.user_data.get('password')
        }
        self.client.login(**user_data)
        data = {'url': 'http://myurl.loc'}
        response = self.client.post('/', data)
        self.assertEqual(response.status_code, 201)
        self.assertIsNotNone(Url.objects.last().account)
        
    def test_shorturls_views__index_url_valid_duplicate(self):
        data = {'url': self.url_str}
        response = self.client.post('/', data)
        self.assertEqual(response.templates[0].name, 'shorturls/exists.html')
        self.assertEqual(response.status_code, 202)

    def test_shorturls_views__index_url_not_valid(self):
        data = {'url': 'not valid url'}
        response = self.client.post('/', data)
        self.assertEqual(response.templates[0].name, 'shorturls/errors.html')
        self.assertEqual(response.status_code, 400)

    def test_shorturls_views__url_redirect_valid(self):
        kwargs = {'shortcode': self.url.shortcode}
        _url = reverse('shorturls:url_redirect', kwargs=kwargs)
        response = self.client.get(_url)
        self.assertEqual(response.status_code, 302)

        referrer = 'http://referrer.ru'
        response = self.client.get(_url, HTTP_REFERER=referrer)
        self.assertEqual(response.status_code, 302)
        referrers = Referrer.objects.filter(url=self.url)
        self.assertEqual(referrers.count(), 1)
        loggings = Logging.objects.filter(referrer=referrers.last())
        self.assertEqual(loggings.count(), 1)

        referrer = 'http://referrer1.ru'
        response = self.client.get(_url, HTTP_REFERER=referrer)
        self.assertEqual(response.status_code, 302)
        referrers = Referrer.objects.filter(url=self.url)
        self.assertEqual(referrers.count(), 2)
        Logging.objects.filter(referrer=referrers.last())
        self.assertEqual(loggings.count(), 1)

    def test_shorturls_views__url_redirect_not_valid(self):
        kwargs = {'shortcode': 'not_valid'}
        _url = reverse('shorturls:url_redirect', kwargs=kwargs)
        response = self.client.get(_url)
        self.assertEqual(response.status_code, 404)
