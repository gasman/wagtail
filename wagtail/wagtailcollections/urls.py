from django.conf.urls import url
from wagtail.wagtailcollections import views


urlpatterns = [
    url(r'^$', views.index, name='wagtailcollections_index'),
]
