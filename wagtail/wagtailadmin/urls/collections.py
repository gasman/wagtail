from django.conf.urls import url

from wagtail.wagtailadmin.views import collections


urlpatterns = [
    url(r'^$', collections.index, name='wagtailadmin_collections_index'),
]
