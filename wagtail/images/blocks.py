import collections

from django import forms
from django.template.loader import render_to_string
from django.utils.functional import cached_property
from django.utils.html import mark_safe

from wagtail.admin.compare import BlockComparison
from wagtail.core.blocks import ChooserBlock

from .shortcuts import get_rendition_or_not_found


class ImageChooserBlock(ChooserBlock):
    @cached_property
    def target_model(self):
        from wagtail.images import get_image_model
        return get_image_model()

    @cached_property
    def widget(self):
        from wagtail.images.widgets import AdminImageChooser
        return AdminImageChooser

    def render_basic(self, value, context=None):
        if value:
            return get_rendition_or_not_found(value, 'original').img_tag()
        else:
            return ''

    def get_comparison_class(self):
        return ImageChooserBlockComparison

    class Meta:
        icon = "image"


class ImageChooserBlockComparison(BlockComparison):
    def htmlvalue(self, val):
        return render_to_string("wagtailimages/widgets/compare.html", {
            'image_a': val,
            'image_b': val,
        })

    def htmldiff(self):
        return render_to_string("wagtailimages/widgets/compare.html", {
            'image_a': self.val_a,
            'image_b': self.val_b,
        })


class ImageBlock(ImageChooserBlock):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.alt_text_field = forms.CharField(widget=forms.Textarea)

    def to_python(self, value):
        # the incoming serialised value should be None, an ID, or a dict of id and alt
        if value is None:
            return value
        elif isinstance(value, collections.abc.Mapping):
            image_id = value['id']
            alt = value['alt']
        else:
            # assume value is an ID
            image_id = value
            alt = None

        try:
            image = self.target_model.objects.get(pk=image_id)
            image.contextual_alt_text = alt
            return image
        except self.target_model.DoesNotExist:
            return None

    def bulk_to_python(self, values):
        """Return the model instances for the given list of primary keys.

        The instances must be returned in the same order as the values and keep None values.
        """
        # TODO: port over the single-query lookup from ChooserBlock
        # objects = self.target_model.objects.in_bulk(values)
        # return [objects.get(id) for id in values]  # Keeps the ordering the same as in values.

        return [self.to_python(value) for value in values]

    def get_prep_value(self, value):
        # the native value (a model instance or None) should serialise to None or a dict of id and alt
        if value is None:
            return None
        else:
            return {'id': value.pk, 'alt': value.contextual_alt_text}

    def render_form(self, value, prefix='', errors=None):
        field = self.field
        widget = field.widget

        widget_attrs = {'id': prefix + '-image', 'placeholder': self.label}
        field_value = field.prepare_value(self.value_for_form(value))

        if hasattr(widget, 'render_with_errors'):
            widget_html = widget.render_with_errors(prefix + '-image', field_value, attrs=widget_attrs, errors=errors)
            widget_has_rendered_errors = True
        else:
            widget_html = widget.render(prefix + '-image', field_value, attrs=widget_attrs)
            widget_has_rendered_errors = False

        alt_text_widget_attrs = {'id': prefix + '-alt', 'rows': 2}
        if value:
            alt_text_field_value = value.contextual_alt_text or value.default_alt_text
        else:
            alt_text_field_value = ''

        alt_text_widget_html = mark_safe('<b>Alt text</b>') + self.alt_text_field.widget.render(prefix + '-alt', alt_text_field_value, attrs=alt_text_widget_attrs)

        return render_to_string('wagtailadmin/block_forms/field.html', {
            'name': self.name,
            'classes': self.meta.classname,
            'widget': widget_html + alt_text_widget_html,
            'field': field,
            'errors': errors if (not widget_has_rendered_errors) else None,
        })

    def value_from_datadict(self, data, files, prefix):
        image = self.value_from_form(self.field.widget.value_from_datadict(data, files, prefix + '-image'))
        alt_text = self.alt_text_field.widget.value_from_datadict(data, files, prefix + '-alt')
        image.contextual_alt_text = alt_text
        return image

    def clean(self, value):
        # HACK: bypass clean, as that nukes contextual_alt_text
        return value
