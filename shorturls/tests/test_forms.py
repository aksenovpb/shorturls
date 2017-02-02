from django.test import TestCase

from shorturls.forms import UrlForm
from shorturls.forms import UrlFullForm
from shorturls.models import Url
from shorturls.validators import validate_url


class ShorturlsFormsTestCase(TestCase):

    def test_shorturls_forms__urlform__valid(self):
        post = {'url': 'ya.ru'}
        form = UrlForm(post)
        self.assertTrue(form.is_valid())
        url = form.cleaned_data.get('url')
        self.assertEqual(url, validate_url(post['url']))

    def test_shorturls_forms__urlform__not_valid(self):
        post_data = {'url': 'notvalid'}
        form = UrlForm(post_data)
        self.assertFalse(form.is_valid())

    def test_shorturls_forms__urlfullform__valid(self):
        post = {'url': 'ya.ru'}
        form = UrlFullForm(post)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data.get('url'), validate_url(post.get('url')))

        post = {'url': 'valid-ya.ru', 'description': 'valid description'}
        form = UrlFullForm(post)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data.get('url'), validate_url(post.get('url')))
        self.assertEqual(form.cleaned_data.get('description'), post.get('description'))
