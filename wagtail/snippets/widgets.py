import json

from django import forms
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from wagtail.admin.admin_url_finder import AdminURLFinder
from wagtail.admin.staticfiles import versioned_static
from wagtail.admin.widgets import BaseChooser
from wagtail.admin.widgets.button import ListingButton
from wagtail.telepath import register
from wagtail.widget_adapters import WidgetAdapter


class AdminSnippetChooser(BaseChooser):
    def __init__(self, model, **kwargs):
        self.model = model
        name = self.model._meta.verbose_name
        self.choose_one_text = _("Choose %s") % name
        self.choose_another_text = _("Choose another %s") % name
        self.link_to_chosen_text = _("Edit this %s") % name

        super().__init__(**kwargs)

    def get_value_data(self, value):
        if value is None:
            return None
        elif isinstance(value, self.model):
            instance = value
        else:  # assume instance ID
            instance = self.model.objects.get(pk=value)

        edit_url = AdminURLFinder().get_edit_url(instance)

        return {
            "id": instance.pk,
            "string": str(instance),
            "edit_url": edit_url,
        }

    def get_context(self, name, value_data, attrs):
        context = super().get_context(name, value_data, attrs)

        chooser_url = reverse(
            "wagtailsnippets:choose",
            args=[
                self.model._meta.app_label,
                self.model._meta.model_name,
            ],
        )

        context.update(
            {
                "display_title": value_data.get("string", ""),
                "chooser_url": chooser_url,
                "icon": "snippet",
                "classname": "snippet-chooser",
            }
        )
        return context

    def render_js_init(self, id_, name, value_data):
        return "createSnippetChooser({id});".format(id=json.dumps(id_))

    @cached_property
    def media(self):
        return forms.Media(
            js=[
                versioned_static("wagtailsnippets/js/snippet-chooser-modal.js"),
                versioned_static("wagtailsnippets/js/snippet-chooser.js"),
            ]
        )


class SnippetChooserAdapter(WidgetAdapter):
    js_constructor = "wagtail.snippets.widgets.SnippetChooser"

    def js_args(self, widget):
        return [
            widget.render_html("__NAME__", None, attrs={"id": "__ID__"}),
            widget.id_for_label("__ID__"),
        ]

    @cached_property
    def media(self):
        return forms.Media(
            js=[
                versioned_static("wagtailsnippets/js/snippet-chooser-telepath.js"),
            ]
        )


register(SnippetChooserAdapter(), AdminSnippetChooser)


class SnippetListingButton(ListingButton):
    pass
