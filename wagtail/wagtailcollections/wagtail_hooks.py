from django.core import urlresolvers
from django.conf.urls import include, url
from django.utils.translation import ugettext_lazy as _

from wagtail.wagtailcore import hooks
from wagtail.wagtailcollections import urls

from wagtail.wagtailadmin.menu import MenuItem


@hooks.register('register_admin_urls')
def register_admin_urls():
    return [
        url(r'^collections/', include(urls)),
    ]


class CollectionsMenuItem(MenuItem):
    def is_shown(self, request):
        return request.user.has_perm('wagtailcollections.change_collection')


@hooks.register('register_settings_menu_item')
def register_collections_menu_item():
    return CollectionsMenuItem(_('Collections'), urlresolvers.reverse('wagtailcollections_index'), classnames='icon icon-collection', order=650)
