from django.conf.urls import url

from wagtail.wagtailadmin.views import collections


urlpatterns = [
    url(r'^$', collections.index, name='index'),
    url(r'^add/$', collections.create, name='add'),
    url(r'^(\d+)/$', collections.edit, name='edit'),
    url(r'^(\d+)/delete/$', collections.delete, name='delete'),
]
