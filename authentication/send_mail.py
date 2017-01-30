from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import six


def send_mail(subject_template_name, email_template_name,
              context, to_email, html_email_template_name=None):

    if isinstance(to_email, six.string_types):
        to_email = [to_email]

    subject = render_to_string(subject_template_name, context)
    # Email subject *must not* contain newlines
    subject = ''.join(subject.splitlines())
    body = render_to_string(email_template_name, context)

    email_message = EmailMultiAlternatives(subject, body, to=[to_email])
    if html_email_template_name is not None:
        html_email = render_to_string(html_email_template_name, context)
        email_message.attach_alternative(html_email, 'text/html')

    email_message.send()