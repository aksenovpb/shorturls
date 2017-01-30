from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import six
from django.utils.crypto import constant_time_compare, salted_hmac
from django.utils.http import base36_to_int, int_to_base36


class UserIsActivateTokenGenerator(PasswordResetTokenGenerator):
    def check_token(self, user, token):
        try:
            ts_b36, hash = token.split('-')
        except ValueError:
            return False

        try:
            ts = base36_to_int(ts_b36)
        except ValueError:
            return False

        if not constant_time_compare(self._make_token_with_timestamp(user, ts), token):
            return False

        if (self._num_days(self._today()) - ts) > settings.PASSWORD_RESET_TIMEOUT_DAYS:
            return False

        return True

    def _make_token_with_timestamp(self, user, timestamp):
        ts_b36 = int_to_base36(timestamp)
        key_salt = 'django.contrib.auth.tokens.PasswordResetTokenGenerator'
        
        if user.date_joined is None:
            joined_timestamp = ''
        else:
            joined_timestamp = user.date_joined.replace(microsecond=0, tzinfo=None)

        value = (six.text_type(user.pk) +
                 six.text_type(joined_timestamp) +
                 six.text_type(timestamp))
        hash = salted_hmac(key_salt, value).hexdigest()[::2]
        return '%s-%s' % (ts_b36, hash)

user_is_active_token_generator = UserIsActivateTokenGenerator()
