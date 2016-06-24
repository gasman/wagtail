from __future__ import absolute_import, unicode_literals

from django import template
from django.template.defaulttags import token_kwargs
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe

from wagtail.wagtailcore import __version__
from wagtail.wagtailcore.models import Page
from wagtail.wagtailcore.rich_text import RichText, expand_db_html

register = template.Library()


@register.simple_tag(takes_context=True)
def pageurl(context, page):
    """
    Outputs a page's URL as relative (/foo/bar/) if it's within the same site as the
    current page, or absolute (http://example.com/foo/bar/) if not.
    """
    return page.relative_url(context['request'].site)


@register.simple_tag(takes_context=True)
def slugurl(context, slug):
    """Returns the URL for the page that has the given slug."""
    page = Page.objects.filter(slug=slug).first()

    if page:
        return page.relative_url(context['request'].site)
    else:
        return None


@register.simple_tag
def wagtail_version():
    return __version__


@register.filter
def richtext(value):
    if isinstance(value, RichText):
        # passing a RichText value through the |richtext filter should have no effect
        return value
    elif value is None:
        html = ''
    else:
        html = expand_db_html(value)

    return mark_safe('<div class="rich-text">' + html + '</div>')


class IncludeBlockNode(template.Node):
    def __init__(self, block_var, extra_context):
        self.block_var = block_var
        self.extra_context = extra_context

    def render(self, context):
        try:
            value = self.block_var.resolve(context)
        except template.VariableDoesNotExist:
            return ''

        if hasattr(value, 'render_as_block'):
            new_context = context.flatten()

            if self.extra_context:
                for var_name, var_value in self.extra_context.items():
                    new_context[var_name] = var_value.resolve(context)

            return value.render_as_block(context=new_context)
        else:
            return force_text(value)


@register.tag
def include_block(parser, token):
    """
    Render the passed item of StreamField content, passing the current template context
    if there's an identifiable way of doing so (i.e. if it has a `render_as_block` method).
    """
    tokens = token.split_contents()

    try:
        tag_name = tokens.pop(0)
        block_var_token = tokens.pop(0)
    except IndexError:
        raise template.TemplateSyntaxError("%r tag requires at least one argument" % tag_name)

    block_var = parser.compile_filter(block_var_token)

    if tokens and tokens[0] == 'with':
        tokens.pop(0)
        extra_context = token_kwargs(tokens, parser)
    else:
        extra_context = None

    if tokens:
        raise template.TemplateSyntaxError("Unexpected argument to %r tag: %r" % (tag_name, tokens[0]))

    return IncludeBlockNode(block_var, extra_context)
