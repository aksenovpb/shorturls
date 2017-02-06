# -*- coding: UTF-8 -*-
import sys

from django.conf import settings
from django.core.management.base import BaseCommand

from helper.send_mail import EmailSender

reload(sys)
sys.setdefaultencoding('utf8')


class Command(BaseCommand):

    def handle(self, *args, **options):
        EmailSender('helper/send_mail/check_mail.html')\
            .render()\
            .send(to=settings.EMAIL_HOST_USER)
