from django.conf import settings
from django.conf.urls import include, url
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.html import format_html, format_html_join
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext

from wagtail.admin.menu import MenuItem
from wagtail.admin.rich_text import HalloPlugin
from wagtail.admin.rich_text.converters.editor_html import LinkTypeRule
from wagtail.admin.search import SearchArea
from wagtail.admin.site_summary import SummaryItem
from wagtail.core import hooks
from wagtail.core.models import BaseViewRestriction
from wagtail.core.wagtail_hooks import require_wagtail_login
from wagtail.documents import admin_urls
from wagtail.documents.api.admin.endpoints import DocumentsAdminAPIEndpoint
from wagtail.documents.forms import GroupDocumentPermissionFormSet
from wagtail.documents.models import get_document_model
from wagtail.documents.permissions import permission_policy
from wagtail.documents.rich_text import DocumentLinkHandler, document_linktype_handler


@hooks.register('register_admin_urls')
def register_admin_urls():
    return [
        url(r'^documents/', include(admin_urls, namespace='wagtaildocs')),
    ]


@hooks.register('construct_admin_api')
def construct_admin_api(router):
    router.register_endpoint('documents', DocumentsAdminAPIEndpoint)


class DocumentsMenuItem(MenuItem):
    def is_shown(self, request):
        return permission_policy.user_has_any_permission(
            request.user, ['add', 'change', 'delete']
        )


@hooks.register('register_admin_menu_item')
def register_documents_menu_item():
    return DocumentsMenuItem(
        _('Documents'),
        reverse('wagtaildocs:index'),
        name='documents',
        classnames='icon icon-doc-full-inverse',
        order=400
    )


@hooks.register('insert_editor_js')
def editor_js():
    js_files = [
        static('wagtaildocs/js/document-chooser.js'),
    ]
    js_includes = format_html_join(
        '\n', '<script src="{0}"></script>',
        ((filename, ) for filename in js_files)
    )
    return js_includes + format_html(
        """
        <script>
            window.chooserUrls.documentChooser = '{0}';
        </script>
        """,
        reverse('wagtaildocs:chooser')
    )


@hooks.register('register_rich_text_features')
def register_document_feature(features):
    features.register_link_type('document', document_linktype_handler)
    features.register_editor_plugin(
        'hallo', 'document-link',
        HalloPlugin(
            name='hallowagtaildoclink',
            js=['wagtaildocs/js/hallo-plugins/hallo-wagtaildoclink.js'],
        )
    )
    features.register_converter_rule('editorhtml', 'document-link', [
        LinkTypeRule('document', DocumentLinkHandler),
    ])
    features.default_features.append('document-link')


class DocumentsSummaryItem(SummaryItem):
    order = 300
    template = 'wagtaildocs/homepage/site_summary_documents.html'

    def get_context(self):
        return {
            'total_docs': get_document_model().objects.count(),
        }

    def is_shown(self):
        return permission_policy.user_has_any_permission(
            self.request.user, ['add', 'change', 'delete']
        )


@hooks.register('construct_homepage_summary_items')
def add_documents_summary_item(request, items):
    items.append(DocumentsSummaryItem(request))


class DocsSearchArea(SearchArea):
    def is_shown(self, request):
        return permission_policy.user_has_any_permission(
            request.user, ['add', 'change', 'delete']
        )


@hooks.register('register_admin_search_area')
def register_documents_search_area():
    return DocsSearchArea(
        _('Documents'), reverse('wagtaildocs:index'),
        name='documents',
        classnames='icon icon-doc-full-inverse',
        order=400)


@hooks.register('register_group_permission_panel')
def register_document_permissions_panel():
    return GroupDocumentPermissionFormSet


@hooks.register('describe_collection_contents')
def describe_collection_docs(collection):
    docs_count = get_document_model().objects.filter(collection=collection).count()
    if docs_count:
        url = reverse('wagtaildocs:index') + ('?collection_id=%d' % collection.id)
        return {
            'count': docs_count,
            'count_text': ungettext(
                "%(count)s document",
                "%(count)s documents",
                docs_count
            ) % {'count': docs_count},
            'url': url,
        }


@hooks.register('before_serve_document')
def check_view_restrictions(document, request):
    """
    Check whether there are any view restrictions on this document which are
    not fulfilled by the given request object. If there are, return an
    HttpResponse that will notify the user of that restriction (and possibly
    include a password / login form that will allow them to proceed). If
    there are no such restrictions, return None
    """
    for restriction in document.collection.get_view_restrictions():
        if not restriction.accept_request(request):
            if restriction.restriction_type == BaseViewRestriction.PASSWORD:
                from wagtail.core.forms import PasswordViewRestrictionForm
                form = PasswordViewRestrictionForm(instance=restriction,
                                                   initial={'return_url': request.get_full_path()})
                action_url = reverse('wagtaildocs_authenticate_with_password', args=[restriction.id])

                password_required_template = getattr(settings, 'DOCUMENT_PASSWORD_REQUIRED_TEMPLATE', 'wagtaildocs/password_required.html')

                context = {
                    'form': form,
                    'action_url': action_url
                }
                return TemplateResponse(request, password_required_template, context)

            elif restriction.restriction_type in [BaseViewRestriction.LOGIN, BaseViewRestriction.GROUPS]:
                return require_wagtail_login(next=request.get_full_path())
