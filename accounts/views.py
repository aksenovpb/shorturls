from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse

from authentication.forms import PasswordChangeForm
from shorturls.forms import UrlFullForm, UrlChangeForm
from shorturls.models import Url


@login_required
def profile(request, template_name='accounts/profile.html'):
    context = {'title': 'Profile'}
    return TemplateResponse(request, template_name, context)


@login_required
def change_password(request, template_name='accounts/change_password.html'):
    from authentication.views import password_change
    return password_change(
        request,
        template_name=template_name,
        post_change_redirect=reverse('accounts:change_password_done'),
        extra_context={'title': 'Password change'}
    )


@login_required
def change_password_done(request, template_name='accounts/change_password_done.html'):
    from authentication.views import password_change_done
    return password_change_done(
        request,
        template_name=template_name,
        extra_context={'title': 'Password change successful'}
    )


@login_required
def urls(request, template_name='accounts/urls.html'):
    qs = Url.objects.filter(account=request.user)
    urls_list = qs.values('id', 'url', 'shortcode', 'description', 'active')
    context = {
        'urls_list': urls_list,
        'title': 'Urls'
    }
    return TemplateResponse(request, template_name, context)


@login_required
def urls_add(request, template_name='accounts/urls_add.html'):
    form = UrlFullForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            instance = form.save(commit=False)
            instance.set_owner(request.user)
            instance.save()
            return HttpResponseRedirect(reverse('accounts:urls_detail', args=(instance.id,)))
        else:
            status = 400
    else:
        status = 200
    context = {
        'form': form,
        'title': 'Url add'
    }
    return TemplateResponse(request, template_name, context, status=status)


@login_required
def urls_detail(request, object_id, template_name='accounts/urls_detail.html'):
    instance = get_object_or_404(Url, pk=object_id, account=request.user)
    context = {
        'instance': instance,
        'title': 'Detail %s' % instance.url
    }
    return TemplateResponse(request, template_name, context)


@login_required
def urls_change(request, object_id, template_name='accounts/urls_change.html'):
    instance = get_object_or_404(Url, pk=object_id, account=request.user)
    form = UrlChangeForm(request.POST or None, instance=instance)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('accounts:urls_detail', args=(instance.id,)))
        else:
            status = 400
    else:
        status = 200
    context = {
        'form': form,
        'title': 'Change %s' % instance.url
    }
    return TemplateResponse(request, template_name, context, status=status)