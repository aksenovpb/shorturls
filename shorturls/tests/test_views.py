from django.test import TestCase
from django.core.urlresolvers import reverse
from shorturls.views import index
from shorturls.models import Url


class ShotrurlsViewsTestCase(TestCase):
    def setUp(self):
        self.url_str = 'ya.ru'
        self.url, created = Url.objects.get_or_create(url=self.url_str)

    def test_shorturls_views__index(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_shorturls_views__index_url_valid(self):
        data = {'url': 'http://yatest.ru'}
        response = self.client.post('/', data)
        self.assertEqual(response.status_code, 201)
        
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
