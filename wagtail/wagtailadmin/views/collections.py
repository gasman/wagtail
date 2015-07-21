from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import permission_required

from wagtail.wagtailcore.models import Collection


@permission_required('wagtailcore.change_collection')
def index(request):
    collections = Collection.objects.order_by('name')

    return render(request, "wagtailadmin/collections/index.html", {
        'collections': collections,
    })


def create(request):
    pass


def edit(request):
    pass


def delete(request):
    pass
