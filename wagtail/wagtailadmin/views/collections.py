from django.contrib.auth.decorators import permission_required
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _

from wagtail.wagtailadmin.forms import CollectionForm
from wagtail.wagtailadmin.views.generic import IndexView, CreateView, EditView, DeleteView
from wagtail.wagtailcore.models import Collection


class Index(IndexView):
    template = 'wagtailadmin/collections/index.html'
    context_object_name = 'collections'

    def get_queryset(self):
        return Collection.objects.order_by('name')

    @method_decorator(permission_required('wagtailcore.change_collection'))
    def get(self, request):
        return super(Index, self).get(request)


class Create(CreateView):
    template = 'wagtailadmin/collections/create.html'
    form_class = CollectionForm
    edit_url_name = 'wagtailadmin_collections:edit'
    index_url_name = 'wagtailadmin_collections:index'

    def get_success_message(self, instance):
        return _("Collection '{0}' created.").format(instance)

    def get_error_message(self):
        return _("The collection could not be created due to errors.")

    @method_decorator(permission_required('wagtailcore.add_collection'))
    def get(self, request):
        return super(Create, self).get(request)

    @method_decorator(permission_required('wagtailcore.add_collection'))
    def post(self, request):
        return super(Create, self).post(request)


class Edit(EditView):
    model = Collection
    context_object_name = 'collection'
    template = 'wagtailadmin/collections/edit.html'
    form_class = CollectionForm
    edit_url_name = 'wagtailadmin_collections:edit'
    index_url_name = 'wagtailadmin_collections:index'

    def get_success_message(self, instance):
        return _("Collection '{0}' updated.").format(instance)

    def get_error_message(self):
        return _("The collection could not be saved due to errors.")

    @method_decorator(permission_required('wagtailcore.change_collection'))
    def get(self, request, instance_id):
        return super(Edit, self).get(request, instance_id)

    @method_decorator(permission_required('wagtailcore.change_collection'))
    def post(self, request, instance_id):
        return super(Edit, self).post(request, instance_id)


class Delete(DeleteView):
    model = Collection
    context_object_name = 'collection'
    template = 'wagtailadmin/collections/confirm_delete.html'
    index_url_name = 'wagtailadmin_collections:index'

    def get_success_message(self, instance):
        return _("Collection '{0}' deleted.").format(instance)

    @method_decorator(permission_required('wagtailcore.delete_collection'))
    def get(self, request, instance_id):
        return super(Delete, self).get(request, instance_id)

    @method_decorator(permission_required('wagtailcore.delete_collection'))
    def post(self, request, instance_id):
        return super(Delete, self).post(request, instance_id)
