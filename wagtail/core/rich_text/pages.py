from django.utils.html import escape

from wagtail.core.models import Page
from wagtail.core.rich_text import LinkHandler
from wagtail.core.rich_text.html_rewriter import ElementRewriter


class PageLinkHandler(LinkHandler):
    identifier = 'page'

    @staticmethod
    def get_model():
        return Page

    @classmethod
    def get_instance(cls, attrs):
        return super().get_instance(attrs).specific

    @classmethod
    def expand_db_attributes(cls, attrs):
        try:
            page = cls.get_instance(attrs)
            return '<a href="%s">' % escape(page.specific.url)
        except Page.DoesNotExist:
            return "<a>"

    @classmethod
    def rewrite_attributes(cls, name, attributes):
        try:
            page = cls.get_instance(attributes)
            return {'href': page.specific.url}
        except Page.DoesNotExist:
            return {}
