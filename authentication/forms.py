from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from django.utils.text import capfirst
from authentication.models import Account

from django.utils.translation import ugettext, ugettext_lazy as _


class RegistrationForm(forms.ModelForm):
    error_messages = {
        'password_mismatch': 'The two password fields didn\'t match.'
    }

    password1 = forms.CharField(label='Password',
        widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation',
        widget=forms.PasswordInput)

    class Meta:
        model = Account
        fields = 'email', 'username'

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch'
            )
        password_validation.validate_password(password2, None)
        return password2

    def save(self, commit=True):
        user = super(RegistrationForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class AuthenticationForm(forms.Form):
    username = forms.CharField(max_length=254)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

    error_messages = {
        'invalid_login': 'Please enter a correct %(username)s and password. '
                         'Note that both fields may be case-sensitive.',
        'inactive': 'This account is inactive'
    }

    def __init__(self, request=None, *args, ** kwargs):
        self.request = request
        self.user_cache = None
        super(AuthenticationForm, self).__init__(*args, **kwargs)

        UserModel = get_user_model()
        self.username_field = UserModel._meta.get_field(UserModel.USERNAME_FIELD)
        if self.fields['username'].label is None:
            self.fields['username'].label = capfirst(self.username_field.verbose_name)
        
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            self.user_cache = authenticate(username=username,
                                           password=password)
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                    params={'username': self.username_field.verbose_name},
                )
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data

    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise forms.ValidationError(
                self.error_messages['inactive'],
                code='inactive'
            )

    def get_user_id(self):
        return self.user_cache.id if self.user_cache else None

    def get_user(self):
        return self.user_cache


class PasswordResetForm(forms.Form):
    email = forms.EmailField(label=_("Email"), max_length=254)

    error_messages = {
        'invalid_email': 'Please enter a correct email. '
                         'Note that both fields may be case-sensitive.'
    }

    def __init__(self, *args, ** kwargs):
        self.user_cache = None
        super(PasswordResetForm, self).__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        self.user_cache = get_user_model().objects.filter(email=email).first()
        if not self.user_cache:
            raise forms.ValidationError(
                self.error_messages['invalid_email'],
                code='invalid_email'
            )

        return email

    def get_user_id(self):
        return self.user_cache.id if self.user_cache else None

    def get_user(self):
        return self.user_cache


    # def send_mail(self, subject_template_name, email_template_name,
    #               context, from_email, to_email, html_email_template_name=None):
    #     """
    #     Sends a django.core.mail.EmailMultiAlternatives to `to_email`.
    #     """
    #     subject = loader.render_to_string(subject_template_name, context)
    #     # Email subject *must not* contain newlines
    #     subject = ''.join(subject.splitlines())
    #     body = loader.render_to_string(email_template_name, context)
    #
    #     email_message = EmailMultiAlternatives(subject, body, from_email, [to_email])
    #     if html_email_template_name is not None:
    #         html_email = loader.render_to_string(html_email_template_name, context)
    #         email_message.attach_alternative(html_email, 'text/html')
    #
    #     email_message.send()
    #
    # def get_users(self, email):
    #     """Given an email, return matching user(s) who should receive a reset.
    #
    #     This allows subclasses to more easily customize the default policies
    #     that prevent inactive users and users with unusable passwords from
    #     resetting their password.
    #     """
    #     active_users = get_user_model()._default_manager.filter(
    #         email__iexact=email, is_active=True)
    #     return (u for u in active_users if u.has_usable_password())
    #
    # def save(self, domain_override=None,
    #          subject_template_name='registration/password_reset_subject.txt',
    #          email_template_name='registration/password_reset_email.html',
    #          use_https=False, token_generator=default_token_generator,
    #          from_email=None, request=None, html_email_template_name=None,
    #          extra_email_context=None):
    #     """
    #     Generates a one-use only link for resetting password and sends to the
    #     user.
    #     """
    #     email = self.cleaned_data["email"]
    #     for user in self.get_users(email):
    #         if not domain_override:
    #             current_site = get_current_site(request)
    #             site_name = current_site.name
    #             domain = current_site.domain
    #         else:
    #             site_name = domain = domain_override
    #         context = {
    #             'email': user.email,
    #             'domain': domain,
    #             'site_name': site_name,
    #             'uid': urlsafe_base64_encode(force_bytes(user.pk)),
    #             'user': user,
    #             'token': token_generator.make_token(user),
    #             'protocol': 'https' if use_https else 'http',
    #         }
    #         if extra_email_context is not None:
    #             context.update(extra_email_context)
    #         self.send_mail(
    #             subject_template_name, email_template_name, context, from_email,
    #             user.email, html_email_template_name=html_email_template_name,
    #         )


class SetPasswordForm(forms.Form):
    """
    A form that lets a user change set their password without entering the old
    password
    """
    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
    }
    new_password1 = forms.CharField(
        label=_("New password"),
        widget=forms.PasswordInput,
        strip=False,
        help_text=password_validation.password_validators_help_text_html(),
    )
    new_password2 = forms.CharField(
        label=_("New password confirmation"),
        strip=False,
        widget=forms.PasswordInput,
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(SetPasswordForm, self).__init__(*args, **kwargs)

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(
                    self.error_messages['password_mismatch'],
                    code='password_mismatch',
                )
        password_validation.validate_password(password2, self.user)
        return password2

    def save(self, commit=True):
        password = self.cleaned_data["new_password1"]
        self.user.set_password(password)
        if commit:
            self.user.save()
        return self.user


class PasswordChangeForm(SetPasswordForm):
    """
    A form that lets a user change their password by entering their old
    password.
    """
    error_messages = dict(SetPasswordForm.error_messages, **{
        'password_incorrect': _("Your old password was entered incorrectly. Please enter it again."),
    })
    old_password = forms.CharField(
        label=_("Old password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autofocus': ''}),
    )

    field_order = ['old_password', 'new_password1', 'new_password2']

    def clean_old_password(self):
        """
        Validates that the old_password field is correct.
        """
        old_password = self.cleaned_data["old_password"]
        if not self.user.check_password(old_password):
            raise forms.ValidationError(
                self.error_messages['password_incorrect'],
                code='password_incorrect',
            )
        return old_password
