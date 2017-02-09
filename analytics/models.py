from __future__ import unicode_literals

from django.db import models

# Create your models here.
from shorturls.models import Url


class ClickEventManager(models.Manager):
    def create_event(self, url_instance):
        if issubclass(url_instance, Url):
            obj, created = self.get_or_create(url=url_instance)
            obj.count += 1
            obj.save()
            return obj


class ClickEvent(models.Model):
    url = models.ForeignKey(Url)
    count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ClickEventManager()

    def __unicode__(self):
        return '%s' % self.count
