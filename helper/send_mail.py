import re

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail as django_send_email
from django.template.loader import render_to_string
from django.utils import six

from helper.function import build_absolute_uri


class SimpleParser:

    result = {}

    def __init__(self, template):
        parse_dict = {}

        index = "_DEFAULT"
        for line in template.split("\n"):
            r = re.search(r"^\[([A-Za-z0-9_]+)\]$", line.strip())
            if r:
                index = r.group(1)
                parse_dict[index] = ""
            else:
                parse_dict[index] += line+"\n"

        self.result = {k: v.strip() for k, v in parse_dict.iteritems()}

    def get(self, key):
        return self.result.get(key)


class EmailSender:

    def __init__(self, template):
        self.template = template

    subject = None
    content = None
    html = None
    template = None

    def render(self, extra_context=None):
        current_site = get_current_site(None)
        context = {
            'site_url': build_absolute_uri(),
            'domain': current_site.domain,
            'site_name': current_site.name,
            'support_url': build_absolute_uri('/feedback/'),
            'unsubscribe_url': build_absolute_uri('/accounts/notifications/')
        }

        if extra_context:
            context.update(extra_context)

        sp = SimpleParser(render_to_string(self.template, context))

        self.subject = sp.get("SUBJECT")
        self.content = sp.get("CONTENT")
        self.html = sp.get("HTML")
        return self

    def send(self, to):
        if not to:
            return

        if isinstance(to, six.string_types):
            to = [to]

        for _to in to:
            django_send_email(self.subject, self.content, settings.EMAIL_HOST_USER, (_to,),
                              html_message=self.html)
