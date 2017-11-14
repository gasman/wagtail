from __future__ import absolute_import, unicode_literals

from django.conf import settings
from django.test import TestCase

from wagtail.wagtailcore.models import Page


class PageSearchTests(object):
    # A TestCase with this class mixed in will be dynamically created
    # for each search backend defined in WAGTAILSEARCH_BACKENDS, with the backend name available
    # as self.backend_name

    # Note that there is currently no provision here for fixture loading or search indexing,
    # which will be required for actually checking the correctness of the results; the current
    # tests just check that `Page.search()` completes without error.

    def test_order_by_title(self):
        list(Page.objects.order_by('title').search('blah', order_by_relevance=False, backend=self.backend_name))

    def test_search_specific_queryset(self):
        list(Page.objects.specific().search('bread', backend=self.backend_name))

    def test_search_specific_queryset_with_fields(self):
        list(Page.objects.specific().search('bread', fields=['title'], backend=self.backend_name))


for backend_name in settings.WAGTAILSEARCH_BACKENDS.keys():
    test_name = "Test%sBackend" % backend_name.title()
    globals()[test_name] = type(test_name, (TestCase, PageSearchTests,), {'backend_name': backend_name})
