from django.contrib.auth.decorators import permission_required
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _

from wagtail.wagtailadmin.forms import CollectionForm
from wagtail.wagtailadmin.views.generic import IndexView, CreateView, EditView, DeleteView
from wagtail.wagtailcore.models import Collection


class Index(IndexView):
    template = 'wagtailadmin/collections/index.html'
    context_object_name = 'collections'
    permission_name = 'wagtailcore.change_collection'

    def get_queryset(self):
        return Collection.objects.order_by('name')


class Create(CreateView):
    template = 'wagtailadmin/collections/create.html'
    form_class = CollectionForm
    edit_url_name = 'wagtailadmin_collections:edit'
    index_url_name = 'wagtailadmin_collections:index'
    permission_name = 'wagtailcore.add_collection'

    def get_success_message(self, instance):
        return _("Collection '{0}' created.").format(instance)

    def get_error_message(self):
        return _("The collection could not be created due to errors.")


class Edit(EditView):
    model = Collection
    context_object_name = 'collection'
    template = 'wagtailadmin/collections/edit.html'
    form_class = CollectionForm
    edit_url_name = 'wagtailadmin_collections:edit'
    index_url_name = 'wagtailadmin_collections:index'
    permission_name = 'wagtailcore.change_collection'

    def get_success_message(self, instance):
        return _("Collection '{0}' updated.").format(instance)

    def get_error_message(self):
        return _("The collection could not be saved due to errors.")


class Delete(DeleteView):
    model = Collection
    context_object_name = 'collection'
    template = 'wagtailadmin/collections/confirm_delete.html'
    index_url_name = 'wagtailadmin_collections:index'
    permission_name = 'wagtailcore.delete_collection'

    def get_success_message(self, instance):
        return _("Collection '{0}' deleted.").format(instance)
