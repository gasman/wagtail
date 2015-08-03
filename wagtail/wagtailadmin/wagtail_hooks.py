from django.core import urlresolvers
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _

from wagtail.wagtailcore import hooks
from wagtail.wagtailadmin.menu import MenuItem, SubmenuMenuItem, settings_menu


class ExplorerMenuItem(MenuItem):
    class Media:
        js = ['wagtailadmin/js/explorer-menu.js']


@hooks.register('register_admin_menu_item')
def register_explorer_menu_item():
    return ExplorerMenuItem(
        _('Explorer'), urlresolvers.reverse('wagtailadmin_explore_root'),
        name='explorer',
        classnames='icon icon-folder-open-inverse dl-trigger',
        attrs={'data-explorer-menu-url': urlresolvers.reverse('wagtailadmin_explorer_nav')},
        order=100)


@hooks.register('register_admin_menu_item')
def register_settings_menu():
    return SubmenuMenuItem(
        _('Settings'), settings_menu, classnames='icon icon-cogs', order=10000)


@hooks.register('register_permissions')
def register_permissions():
    return Permission.objects.filter(content_type__app_label='wagtailadmin', codename='access_admin')


class CollectionsMenuItem(MenuItem):
    def is_shown(self, request):
        return request.user.has_perm('wagtailcore.change_collection')


@hooks.register('register_settings_menu_item')
def register_collections_menu_item():
    return CollectionsMenuItem(_('Collections'), urlresolvers.reverse('wagtailadmin_collections:index'), classnames='icon icon-collection', order=650)


@hooks.register('register_permissions')
def register_collection_permissions():
    collection_content_type = ContentType.objects.get(app_label='wagtailcore', model='collection')
    collection_permissions = Permission.objects.filter(content_type=collection_content_type)
    return collection_permissions
