from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME, update_session_auth_hash
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import resolve_url
from django.template.response import TemplateResponse
from django.utils.encoding import force_bytes
from django.utils.encoding import force_text
from django.utils.http import is_safe_url
from django.utils.http import urlsafe_base64_decode
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_protect

from authentication.forms import AuthenticationForm
from authentication.forms import RegistrationForm, PasswordResetForm, SetPasswordForm, PasswordChangeForm
from authentication.tokens import user_is_active_token_generator
from helper.function import build_absolute_uri
from helper.send_mail import EmailSender

USER_IS_ACTIVE = getattr(settings, 'AUTHENTICATION_USER_IS_ACTIVE', True)
LOGIN_BEFORE_REG = getattr(settings, 'AUTHENTICATION_LOGIN_BEFORE_REG', True)
REDIRECT_BEFORE_REG = getattr(settings, 'AUTHENTICATION_REDIRECT_BEFORE_REG', '/')


def signup(request,
           template_name='authentication/registration.html',
           template_mail_user_is_activate='authentication/mails/registration_user_is_active.html',
           template_mail_user_not_is_activate='authentication/mails/registration_user_not_is_active.html',
           registration_form=RegistrationForm,
           redirect_field_name=REDIRECT_FIELD_NAME,
           extra_context=None):
    
    redirect_to = request.POST.get(redirect_field_name,
                                   request.GET.get(redirect_field_name, ''))

    form = registration_form(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            user = get_user_model().objects.create_user(
                form.cleaned_data.get('username'),
                form.cleaned_data.get('email'),
                form.cleaned_data.get('password1')
            )

            email_context = {'user': user, 'host': request.get_host()}

            if USER_IS_ACTIVE:
                template_message = template_mail_user_is_activate

                if LOGIN_BEFORE_REG:
                    user = authenticate(
                            username=form.cleaned_data.get(get_user_model().USERNAME_FIELD),
                            password=form.cleaned_data.get('password1')
                        )
                    auth_login(request, user)
            else:
                user.is_active = False
                user.save()

                email_context.update(
                    {
                        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                        'user': user,
                        'token': user_is_active_token_generator.make_token(user),
                    }
                )

                template_message = template_mail_user_not_is_activate

            EmailSender(template_message).render(email_context).send(to=user.email)

            if not is_safe_url(url=redirect_to, host=request.get_host()):
                redirect_to = REDIRECT_BEFORE_REG

            return HttpResponseRedirect(redirect_to)

        else:
            status = 400
    else:
        status = 200

    context = {
        'login_url': resolve_url(settings.LOGIN_URL),
        'title': 'Registration',
        'form': form
    }

    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context, status=status)


def login(request,
          template_name='authentication/login.html',
          redirect_field_name=REDIRECT_FIELD_NAME,
          authentication_form=AuthenticationForm,
          extra_context=None):
    redirect_to = request.POST.get(redirect_field_name,
                                   request.GET.get(redirect_field_name, ''))

    if request.method == 'POST':
        form = authentication_form(request, data=request.POST)
        if form.is_valid():
            if not is_safe_url(url=redirect_to, host=request.get_host()):
                redirect_to = resolve_url(settings.LOGIN_REDIRECT_URL)
            auth_login(request, form.get_user())

            return HttpResponseRedirect(redirect_to)
        else:
            status = 400
    else:
        status = 200
        form = authentication_form(request)

    current_site = get_current_site(request)

    context = {
        'form': form,
        redirect_field_name: redirect_to,
        'site': current_site,
        'site_name': current_site.name,
        'title': 'Login',
    }

    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context, status=status)


def logout(request,
           template_name='authentication/logout.html',
           redirect_field_name=REDIRECT_FIELD_NAME,
           next_page=None,
           extra_context=None):
    auth_logout(request)

    if next_page is not None:
        next_page = resolve_url(next_page)

    if redirect_field_name in request.POST or redirect_field_name in request.GET:
        next_page = request.POST.get(redirect_field_name, request.GET.get(redirect_field_name))

        if not is_safe_url(url=next_page, host=request.get_host()):
            next_page = request.path

    if next_page:
        return HttpResponseRedirect(next_page)

    current_site = get_current_site(request)
    context = {
        'site': current_site,
        'site_name': current_site.name,
        'title': 'Logged out'
    }

    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


def activate(request, uidb64=None, token=None, template_name='authentication/activate.html', extra_context=None):
    UserModel = get_user_model()
    assert uidb64 is not None and token is not None  # checked by URLconf

    try:
        # urlsafe_base64_decode() decodes to bytestring on Python 3
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = UserModel._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
        user = None

    if user is not None and user_is_active_token_generator.check_token(user, token):
        validlink = True
        title = 'User activated'
        user.is_activate = True
        user.save()
        status = 200
    else:
        validlink = False
        title = 'User not found'
        status = 400
    context = {
        'title': title,
        'validlink': validlink,
    }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context, status=status)


def password_reset(request,
                   template_name='authenticate/password_reset_form.html',
                   template_mail_password_reset='authenticate/password_reset_email.html',
                   template_mail_subject='authenticate/password_reset_subject.txt',
                   password_reset_form=PasswordResetForm,
                   token_generator=default_token_generator,
                   post_reset_redirect=None,
                   from_email=None,
                   extra_context=None,
                   html_email_template_name=None,
                   extra_email_context=None):

    if post_reset_redirect is None:
        post_reset_redirect = reverse('password_reset_done')
    else:
        post_reset_redirect = resolve_url(post_reset_redirect)
    if request.method == "POST":
        form = password_reset_form(request.POST)
        if form.is_valid():
            opts = {
                'use_https': request.is_secure(),
                'token_generator': token_generator,
                'from_email': from_email,
                'email_template_name': template_mail_password_reset,
                'subject_template_name': template_mail_subject,
                'request': request,
                'html_email_template_name': html_email_template_name,
                'extra_email_context': extra_email_context,
            }
            form.save(**opts)
            return HttpResponseRedirect(post_reset_redirect)
    else:
        form = password_reset_form()
    context = {
        'form': form,
        'title': _('Password reset'),
    }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


def password_reset_done(request,
                        template_name='authenticate/password_reset_done.html',
                        extra_context=None):
    context = {
        'title': _('Password reset sent'),
    }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


# @never_cache
def password_reset_confirm(request, uidb64=None, token=None,
                           template_name='authenticate/password_reset_confirm.html',
                           token_generator=default_token_generator,
                           set_password_form=SetPasswordForm,
                           post_reset_redirect=None,
                           extra_context=None):

    UserModel = get_user_model()
    assert uidb64 is not None and token is not None  # checked by URLconf
    if post_reset_redirect is None:
        post_reset_redirect = reverse('password_reset_complete')
    else:
        post_reset_redirect = resolve_url(post_reset_redirect)
    try:
        # urlsafe_base64_decode() decodes to bytestring on Python 3
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = UserModel._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
        user = None

    if user is not None and token_generator.check_token(user, token):
        validlink = True
        title = _('Enter new password')
        if request.method == 'POST':
            form = set_password_form(user, request.POST)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(post_reset_redirect)
        else:
            form = set_password_form(user)
    else:
        validlink = False
        form = None
        title = _('Password reset unsuccessful')
    context = {
        'form': form,
        'title': title,
        'validlink': validlink,
    }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


def password_reset_complete(request,
                            template_name='authenticate/password_reset_complete.html',
                            extra_context=None):
    context = {
        'login_url': resolve_url(settings.LOGIN_URL),
        'title': _('Password reset complete'),
    }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


@csrf_protect
@login_required
def password_change(request,
                    template_name='authenticate/password_change_form.html',
                    post_change_redirect=None,
                    password_change_form=PasswordChangeForm,
                    extra_context=None):
    if post_change_redirect is None:
        post_change_redirect = reverse('password_change_done')
    else:
        post_change_redirect = resolve_url(post_change_redirect)
    if request.method == "POST":
        form = password_change_form(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            # Updating the password logs out all other sessions for the user
            # except the current one if
            # django.contrib.auth.middleware.SessionAuthenticationMiddleware
            # is enabled.
            update_session_auth_hash(request, form.user)
            return HttpResponseRedirect(post_change_redirect)
        else:
            status = 400
    else:
        form = password_change_form(user=request.user)
        status = 200
    context = {
        'form': form,
        'title': _('Password change'),
    }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context, status=status)


@login_required
def password_change_done(request,
                         template_name='authenticate/password_change_done.html',
                         extra_context=None):
    context = {
        'title': _('Password change successful'),
    }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)
