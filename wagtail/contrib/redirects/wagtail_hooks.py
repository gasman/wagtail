from django.contrib.auth.models import Permission
from django.urls import include, path, reverse
from django.utils.translation import gettext_lazy as _

from wagtail.admin.menu import MenuItem
from wagtail.contrib.redirects import urls
from wagtail.contrib.redirects.permissions import permission_policy
from wagtail.core import hooks
from wagtail.core.log_actions import registry as log_action_registry

from .models import Redirect


class RedirectAdminURLFinder:
    def __init__(self, user):
        self.user_can_edit = permission_policy.user_has_permission(user, 'change')

    def get_edit_url(self, log_entry):
        if self.user_can_edit:
            return reverse('wagtailredirects:edit', args=(log_entry.object_id, ))
        else:
            return None


@hooks.register('register_admin_urls')
def register_admin_urls():
    log_action_registry.register_admin_url_finder(Redirect, RedirectAdminURLFinder)
    return [
        path('redirects/', include(urls, namespace='wagtailredirects')),
    ]


class RedirectsMenuItem(MenuItem):
    def is_shown(self, request):
        return permission_policy.user_has_any_permission(
            request.user, ['add', 'change', 'delete']
        )


@hooks.register('register_settings_menu_item')
def register_redirects_menu_item():
    return RedirectsMenuItem(
        _('Redirects'), reverse('wagtailredirects:index'), icon_name='redirect', order=800
    )


@hooks.register('register_permissions')
def register_permissions():
    return Permission.objects.filter(content_type__app_label='wagtailredirects',
                                     codename__in=['add_redirect', 'change_redirect', 'delete_redirect'])
