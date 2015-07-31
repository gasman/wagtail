from django.utils.translation import ugettext_lazy as _

from wagtail.wagtailadmin.forms import CollectionForm
from wagtail.wagtailadmin.views.generic import IndexView, CreateView, EditView, DeleteView
from wagtail.wagtailcore.models import Collection


class Index(IndexView):
    model = Collection
    default_order = 'name'
    template = 'wagtailadmin/collections/index.html'
    context_object_name = 'collections'
    url_namespace = 'wagtailadmin_collections'
    header_icon = 'collection'

    page_title = _("Collections")
    add_item_label = _("Add a collection")

    data_columns = [
        ('name', _("Collection")),
    ]


class Create(CreateView):
    model = Collection
    form_class = CollectionForm
    url_namespace = 'wagtailadmin_collections'
    header_icon = 'collection'

    page_title = _("Add collection")
    success_message = _("Collection '{0}' created.")
    error_message = _("The collection could not be created due to errors.")


class Edit(EditView):
    model = Collection
    context_object_name = 'collection'
    form_class = CollectionForm
    url_namespace = 'wagtailadmin_collections'
    header_icon = 'collection'

    success_message = _("Collection '{0}' updated.")
    error_message = _("The collection could not be saved due to errors.")
    delete_item_label = _("Delete collection")


class Delete(DeleteView):
    model = Collection
    context_object_name = 'collection'
    url_namespace = 'wagtailadmin_collections'
    header_icon = 'collection'

    page_title = _("Delete collection")
    confirmation_message = _("Are you sure you want to delete this collection?")
    success_message = _("Collection '{0}' deleted.")
