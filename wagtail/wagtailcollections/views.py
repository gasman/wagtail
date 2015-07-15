from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import permission_required

from wagtail.wagtailcollections.models import Collection


@permission_required('wagtailcollections.change_collection')
def index(request):
    collections = Collection.objects.order_by('name')

    return render(request, "wagtailcollections/index.html", {
        'collections': collections,
    })
