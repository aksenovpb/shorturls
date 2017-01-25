from django.test import TestCase
from django.core.validators import ValidationError
from django.core.validators import URLValidator
from shorturls.validators import validate_url


class ShorturlsValidatorsTestCase(TestCase):
    def test_shorturls_validators__validate_url_valid(self):
        url = 'google.com'
        self.assertEqual(validate_url('http://'+url), 'http://'+url)
        self.assertEqual(validate_url(url), 'http://'+url)

    def test_shorturls_validators__validate_url_not_valid(self):
        url = 'notvalid'
        with self.assertRaises(ValidationError) as e:
            validate_url(url)

        self.assertEqual(e.exception.code, URLValidator.code)
