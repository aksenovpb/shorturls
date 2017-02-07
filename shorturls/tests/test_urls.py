from django.test import TestCase
from django.core.urlresolvers import reverse


class ShorturlsUrlsTestCase(TestCase):
    def test_shorturls_urls(self): 
        self.assertEqual(reverse('shorturls:index'), '/')
