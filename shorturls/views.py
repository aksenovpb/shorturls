from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.template.response import TemplateResponse

from shorturls.forms import UrlForm
from shorturls.models import Url, Referrer, Logging


def index(request):
    form = UrlForm(request.POST or None)
    context = {}

    if request.method == 'POST':
        if form.is_valid():
            url = form.cleaned_data.get('url')
            account = request.user if request.user.is_authenticated() else None
            obj, created = Url.objects.get_or_create(url=url, account=account)
            context.update({
                'object': obj,
                'created': created
            })
            if created:
                template = 'shorturls/success.html'
                status = 201
            else:
                template = 'shorturls/exists.html'
                status = 202
        else:
            template = 'shorturls/errors.html'
            status = 400
    else:
        template = 'shorturls/index.html'
        status = 200

    context.update({
        'form': form
    })
    return TemplateResponse(request, template, context, status=status)


def url_redirect(request, shortcode):
    url = get_object_or_404(Url, shortcode=shortcode)
    if request.META.get('HTTP_REFERER'):
        form = UrlForm({'url': request.META.get('HTTP_REFERER')})
        if form.is_valid():
            valid_referrer = form.cleaned_data.get('url')
            referrer, create = Referrer.objects.get_or_create(url=url, referrer=valid_referrer)
            Logging(referrer=referrer).save()
    return redirect(url.url)
