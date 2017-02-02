from django.conf.urls import url
from accounts import views


urlpatterns = [
    url(r'^profile/$', views.profile, name='profile'),
    url(r'^change_password/$', views.change_password, name='change_password'),
    url(r'^change_password/done/$', views.change_password_done, name='change_password_done'),
    url(r'^urls/$', views.urls, name='urls'),
    url(r'^urls/add/$', views.urls_add, name='urls_add'),
    url(r'^urls/(?P<object_id>[0-9]+)/detail/$', views.urls_detail, name='urls_detail'),
    url(r'^urls/(?P<object_id>[0-9]+)/change/$', views.urls_change, name='urls_change'),
]
