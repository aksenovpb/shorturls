from __future__ import unicode_literals

from django.conf import settings
from django.db import models

from authentication.models import Account
from shorturls.validators import validate_url
from shorturls.utils import create_shortcode


SHORTCODE_MAX = getattr(settings, 'SHORTCODE_MAX', 15)


class Url(models.Model):
    url = models.CharField(max_length=220, validators=[validate_url])
    description = models.TextField(null=True)
    shortcode = models.CharField(max_length=SHORTCODE_MAX, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)
    account = models.ForeignKey(settings.AUTH_USER_MODEL, null=True)

    def save(self, *args, **kwargs):
        if self.shortcode is None or self.shortcode == '':
            self.shortcode = create_shortcode(self)
        if not self.url.startswith('http'):
            self.url = 'http://' + self.url
        super(Url, self).save(*args, **kwargs)

    def __unicode__(self):
        return u'%s' % self.url

    def __str__(self):
        return self.url

    def set_owner(self, account):
        self.account = account


class Referrer(models.Model):
    url = models.ForeignKey(Url)
    referrer = models.CharField(max_length=220, validators=[validate_url], blank=True)


class Logging(models.Model):
    referrer = models.ForeignKey(Referrer)
    go_at = models.DateTimeField(auto_now_add=True)
