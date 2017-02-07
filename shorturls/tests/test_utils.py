import re

from django.test import TestCase
from shorturls import utils
from shorturls.models import Url


class ShorturlsUtilsTestCase(TestCase):
    def test_shorturls_utils__create_shortcode(self):
        new_code = utils.create_shortcode(Url())
        self.assertIsNotNone(re.match(r'[a-zA-Z0-9]{%s,}' % utils.SHORTCODE_MIN, new_code))
