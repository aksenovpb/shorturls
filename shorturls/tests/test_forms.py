from django.test import TestCase

from shorturls.forms import UrlForm
from shorturls.validators import validate_url


class ShorturlsFormsTestCase(TestCase):

    def test_shorturls_forms__urlform__valid(self):
        post_data = {'url': 'ya.ru'}
        form = UrlForm(post_data)
        self.assertTrue(form.is_valid())
        url = form.cleaned_data.get('url')
        self.assertEqual(url, validate_url(post_data['url']))

    def test_shorturls_forms__urlform__not_valid(self):
        post_data = {'url': 'notvalid'}
        form = UrlForm(post_data)
        self.assertFalse(form.is_valid())
