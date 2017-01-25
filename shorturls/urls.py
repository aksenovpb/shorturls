from django.conf.urls import url
from shorturls import views


urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<shortcode>[\w]+)/$', views.url_redirect, name='url_redirect')
]
