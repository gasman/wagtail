from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import permission_required
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from wagtail.wagtailadmin.forms import CollectionForm
from wagtail.wagtailadmin import messages
from wagtail.wagtailcore.models import Collection


@permission_required('wagtailcore.change_collection')
def index(request):
    collections = Collection.objects.order_by('name')

    return render(request, "wagtailadmin/collections/index.html", {
        'collections': collections,
    })


@permission_required('wagtailcore.add_collection')
def create(request):
    if request.method == 'POST':
        form = CollectionForm(request.POST)
        if form.is_valid():
            collection = form.save()
            messages.success(request, _("Collection '{0}' created.").format(collection), buttons=[
                messages.button(reverse('wagtailadmin_collections:edit', args=(collection.id,)), _('Edit'))
            ])
            return redirect('wagtailadmin_collections:index')
        else:
            messages.error(request, _("The collection could not be created due to errors."))
    else:
        form = CollectionForm()

    return render(request, 'wagtailadmin/collections/create.html', {
        'form': form,
    })


@permission_required('wagtailcore.change_collection')
def edit(request, collection_id):
    collection = get_object_or_404(Collection, id=collection_id)

    if request.POST:
        form = CollectionForm(request.POST, instance=collection)
        if form.is_valid():
            collection = form.save()
            messages.success(request, _("Collection '{0}' updated.").format(collection), buttons=[
                messages.button(reverse('wagtailadmin_collections:edit', args=(collection.id,)), _('Edit'))
            ])
            return redirect('wagtailadmin_collections:index')
        else:
            messages.error(request, _("The collection could not be saved due to errors."))
    else:
        form = CollectionForm(instance=collection)

    return render(request, 'wagtailadmin/collections/edit.html', {
        'collection': collection,
        'form': form,
    })


@permission_required('wagtailcore.delete_collection')
def delete(request, collection_id):
    collection = get_object_or_404(Collection, id=collection_id)

    if request.POST:
        collection.delete()
        messages.success(request, _("Collection '{0}' deleted.").format(collection))
        return redirect('wagtailadmin_collections:index')

    return render(request, "wagtailadmin/collections/confirm_delete.html", {
        'collection': collection,
    })
