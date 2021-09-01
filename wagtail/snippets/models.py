from django.contrib.admin.utils import quote
from django.core import checks
from django.urls import reverse

from wagtail.admin.checks import check_panels_in_model
from wagtail.admin.models import get_object_usage
from wagtail.core.log_actions import registry as log_action_registry


SNIPPET_MODELS = []


def get_snippet_models():
    return SNIPPET_MODELS


def register_snippet(model):
    if model not in SNIPPET_MODELS:
        model.get_usage = get_object_usage
        model.usage_url = get_snippet_usage_url
        SNIPPET_MODELS.append(model)
        SNIPPET_MODELS.sort(key=lambda x: x._meta.verbose_name)

        # Set up the mapping for the log framework to translate log entries for a snippet model
        # into the URL where a user can edit that model instance, provided they have permission
        app_label = model._meta.app_label
        model_name = model._meta.model_name

        class SnippetAdminURLFinder:
            def __init__(self, user):
                from wagtail.snippets.permissions import get_permission_name
                self.user_can_edit = user.has_perm(get_permission_name('change', model))

            def get_edit_url(self, log_entry):
                if self.user_can_edit:
                    return reverse(
                        'wagtailsnippets:edit',
                        args=(app_label, model_name, quote(log_entry.object_id))
                    )
                else:
                    return None

        log_action_registry.register_admin_url_finder(model, SnippetAdminURLFinder)

        @checks.register('panels')
        def modeladmin_model_check(app_configs, **kwargs):
            errors = check_panels_in_model(model, 'snippets')
            return errors

    return model


def get_snippet_usage_url(self):
    return reverse('wagtailsnippets:usage', args=(
        self._meta.app_label, self._meta.model_name, quote(self.pk)))
