from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import permission_required
from django.core.urlresolvers import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.views.generic.base import View

from wagtail.wagtailadmin.forms import CollectionForm
from wagtail.wagtailadmin import messages
from wagtail.wagtailcore.models import Collection


class Index(View):
    @method_decorator(permission_required('wagtailcore.change_collection'))
    def get(self, request):
        collections = Collection.objects.order_by('name')

        return render(request, "wagtailadmin/collections/index.html", {
            'collections': collections,
        })


class Create(View):
    @method_decorator(permission_required('wagtailcore.add_collection'))
    def get(self, request):
        self.form = CollectionForm()
        return self.render_to_response()

    @method_decorator(permission_required('wagtailcore.add_collection'))
    def post(self, request):
        self.form = CollectionForm(request.POST)
        if self.form.is_valid():
            collection = self.form.save()
            messages.success(request, _("Collection '{0}' created.").format(collection), buttons=[
                messages.button(reverse('wagtailadmin_collections:edit', args=(collection.id,)), _('Edit'))
            ])
            return redirect('wagtailadmin_collections:index')
        else:
            messages.error(request, _("The collection could not be created due to errors."))
            return self.render_to_response()

    def render_to_response(self):
        return render(self.request, 'wagtailadmin/collections/create.html', {
            'form': self.form,
        })


class Edit(View):
    @method_decorator(permission_required('wagtailcore.change_collection'))
    def get(self, request, collection_id):
        self.collection = get_object_or_404(Collection, id=collection_id)
        self.form = CollectionForm(instance=self.collection)
        return self.render_to_response()

    @method_decorator(permission_required('wagtailcore.change_collection'))
    def post(self, request, collection_id):
        self.collection = get_object_or_404(Collection, id=collection_id)

        self.form = CollectionForm(request.POST, instance=self.collection)
        if self.form.is_valid():
            self.form.save()
            messages.success(request, _("Collection '{0}' updated.").format(self.collection), buttons=[
                messages.button(reverse('wagtailadmin_collections:edit', args=(self.collection.id,)), _('Edit'))
            ])
            return redirect('wagtailadmin_collections:index')
        else:
            messages.error(request, _("The collection could not be saved due to errors."))
            return self.render_to_response()

    def render_to_response(self):
        return render(self.request, 'wagtailadmin/collections/edit.html', {
            'collection': self.collection,
            'form': self.form,
        })


class Delete(View):
    @method_decorator(permission_required('wagtailcore.delete_collection'))
    def get(self, request, collection_id):
        collection = get_object_or_404(Collection, id=collection_id)
        return render(request, "wagtailadmin/collections/confirm_delete.html", {
            'collection': collection,
        })

    @method_decorator(permission_required('wagtailcore.delete_collection'))
    def post(self, request, collection_id):
        collection = get_object_or_404(Collection, id=collection_id)

        collection.delete()
        messages.success(request, _("Collection '{0}' deleted.").format(collection))
        return redirect('wagtailadmin_collections:index')
