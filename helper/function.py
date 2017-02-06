import os

from django.contrib.sites.models import Site


def build_absolute_uri(path='/', **kwargs):
    from django.utils.http import urlencode

    return '%s://%s%s%s%s' % ('https' if os.environ.get("HTTPS") else 'http',
                              Site.objects.get_current(),
                              path,
                              '?' if kwargs else '',
                              urlencode(kwargs))