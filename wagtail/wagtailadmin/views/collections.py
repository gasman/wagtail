from django.utils.translation import ugettext_lazy as _

from wagtail.wagtailadmin.forms import CollectionForm
from wagtail.wagtailadmin.views.generic import IndexView, CreateView, EditView, DeleteView
from wagtail.wagtailcore.models import Collection


class Index(IndexView):
    model = Collection
    default_order = 'name'
    template = 'wagtailadmin/collections/index.html'
    context_object_name = 'collections'
    permission_name = 'wagtailcore.change_collection'
    add_permission_name = 'wagtailcore.add_collection'
    add_url_name = 'wagtailadmin_collections:add'
    index_url_name = 'wagtailadmin_collections:index'
    header_icon = 'collection'

    page_title = _("Collections")
    add_item_label = _("Add a collection")

    data_columns = [
        ('name', _("Collection")),
    ]


class Create(CreateView):
    template = 'wagtailadmin/collections/create.html'
    form_class = CollectionForm
    edit_url_name = 'wagtailadmin_collections:edit'
    index_url_name = 'wagtailadmin_collections:index'
    permission_name = 'wagtailcore.add_collection'

    success_message = _("Collection '{0}' created.")
    error_message = _("The collection could not be created due to errors.")


class Edit(EditView):
    model = Collection
    context_object_name = 'collection'
    template = 'wagtailadmin/collections/edit.html'
    form_class = CollectionForm
    edit_url_name = 'wagtailadmin_collections:edit'
    index_url_name = 'wagtailadmin_collections:index'
    permission_name = 'wagtailcore.change_collection'

    success_message = _("Collection '{0}' updated.")
    error_message = _("The collection could not be saved due to errors.")


class Delete(DeleteView):
    model = Collection
    context_object_name = 'collection'
    template = 'wagtailadmin/collections/confirm_delete.html'
    index_url_name = 'wagtailadmin_collections:index'
    permission_name = 'wagtailcore.delete_collection'

    success_message = _("Collection '{0}' deleted.")
