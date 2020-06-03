from collections import defaultdict
from collections.abc import Mapping
import html
import re
import warnings

from django.utils.html import conditional_escape, format_html
from django.utils.safestring import mark_safe


ELEMENT_SELECTOR = re.compile(r'^([\w-]+)$')
ELEMENT_WITH_ATTR_SELECTOR = re.compile(r'^([\w-]+)\[([\w-]+)\]$')
ELEMENT_WITH_ATTR_EXACT_SINGLE_QUOTE_SELECTOR = re.compile(r"^([\w-]+)\[([\w-]+)='(.*)'\]$")
ELEMENT_WITH_ATTR_EXACT_DOUBLE_QUOTE_SELECTOR = re.compile(r'^([\w-]+)\[([\w-]+)="(.*)"\]$')
ELEMENT_WITH_ATTR_EXACT_UNQUOTED_SELECTOR = re.compile(r"^([\w-]+)\[([\w-]+)=([\w-]+)\]$")

DOUBLE_QUOTED_ATTRIBUTE = r'([\w-]+)\="([^"]*)"'
SINGLE_QUOTED_ATTRIBUTE = r"([\w-]+)\='([^]*)'"
UNQUOTED_ATTRIBUTE = r'([\w-]+)\=([\w-]+)'
ATTRIBUTE = re.compile(
    r'(?:%s|%s|%s)' % (DOUBLE_QUOTED_ATTRIBUTE, SINGLE_QUOTED_ATTRIBUTE, UNQUOTED_ATTRIBUTE)
)


class Rule:
    """A CSS-like rule that an HTML element can match or not"""
    priority = None

    def __lt__(self, other):
        # Define an ordering on Selector objects so that running sort() on a list of them
        # orders by priority
        return self.priority < other.priority


class ElementRule(Rule):
    priority = 2  # lower than an element-with-attribute rule

    def __init__(self, name, rewriter):
        self.name = name
        self.rewriter = rewriter

    def attributes_match(self, attrs):
        # this rule does not care about attributes
        return True


class ElementWithAttributeRule(Rule):
    priority = 1  # higher than element rule

    def __init__(self, name, attr, rewriter):
        self.name = name
        self.attr = attr
        self.rewriter = rewriter

    def attributes_match(self, attrs):
        return self.attr in attrs


class ElementWithAttributeExactRule(Rule):
    priority = 1  # higher than element rule

    def __init__(self, name, attr, value, rewriter):
        self.name = name
        self.attr = attr
        self.value = value
        self.rewriter = rewriter

    def attributes_match(self, attrs):
        return (self.attr in attrs) and (attrs[self.attr] == self.value)


class HTMLRewriter:
    def __init__(self, rules):
        self.rules_by_element = defaultdict(list)
        self.add_rules(rules)

    def add_rules(self, rules):
        # accepts either a dict of {selector: rewriter}, or a list of (selector, rewriter) tuples
        if isinstance(rules, Mapping):
            rules = rules.items()

        for selector, rewriter in rules:
            self.add_rule(selector, rewriter)

    def add_rule(self, selector, rewriter):
        match = ELEMENT_SELECTOR.match(selector)
        if match:
            name = match.group(1)
            self.rules_by_element[name].append(
                ElementRule(name, rewriter)
            )
            self.rules_by_element[name].sort()
            return

        match = ELEMENT_WITH_ATTR_SELECTOR.match(selector)
        if match:
            name, attr = match.groups()
            self.rules_by_element[name].append(
                ElementWithAttributeRule(name, attr, rewriter)
            )
            self.rules_by_element[name].sort()
            return

        for regex in (
            ELEMENT_WITH_ATTR_EXACT_SINGLE_QUOTE_SELECTOR,
            ELEMENT_WITH_ATTR_EXACT_DOUBLE_QUOTE_SELECTOR,
            ELEMENT_WITH_ATTR_EXACT_UNQUOTED_SELECTOR
        ):
            match = regex.match(selector)
            if match:
                name, attr, value = match.groups()
                self.rules_by_element[name].append(
                    ElementWithAttributeExactRule(name, attr, value, rewriter)
                )
                self.rules_by_element[name].sort()
                return

        warnings.warn("Unsupported selector format: %r" % selector)

    def rewrite(self, html):
        """
        Rewrite a string of HTML according to the configured rules
        """
        result, _ = self._rewrite(html)
        return result

    def _rewrite(self, html, *, start=0, until_tag=None):
        """
        Internal method used recursively by `rewrite`.
        Rewrites a string of HTML, starting from offset `start`, until it encounters either the end
        of the string, or a closing tag as specified in `until_tag` that is NOT balanced by an
        opening tag seen in the current invocation of `_rewrite`.

        In other words,

            some text with <span>an extra span</span> in it</span>
                                                           ^^^^^^^ this one.

        Upon reaching either end condition (closing tag or end of string), it will return a tuple
        of the rewritten HTML string and the offset of any subsequent not-yet-processed HTML.
        """

        if not self.rules_by_element:
            # no rewrite rules, so nothing to do. Yay!
            return mark_safe(html[start:]), len(html)

        position = start  # current position within the html string
        result = ''  # rewritten HTML goes here

        # the number of pending occurrences of until_tag that we will skip past before treating it
        # as the ACTUAL closing tag
        ignored_closing_tag_count = 0

        # build a regexp that matches any element name in our rule list,
        # e.g. "(h1|a|embed)"
        element_name_re = "(%s)" % (
            '|'.join(re.escape(name) for name in self.rules_by_element.keys())
        )

        # turn this into a regexp that matches any opening tag with one of these names
        # and any set of attributes - e.g. "<(h1|a|embed)(\b[^>]*)>"
        opening_tag_re = r'<%s(\b[^>]*)>' % element_name_re

        if until_tag:
            # our final regexp also needs to match the specified closing tag
            closing_tag_re = r'</(%s)>' % re.escape(until_tag)
            final_re_expr = r'(?:%s|%s)' % (opening_tag_re, closing_tag_re)
        else:
            # no until_tag specified, so we're just looking for opening tags
            final_re_expr = opening_tag_re

        # we need to compile the regexp to be able to start the search from an arbitrary offset
        final_re = re.compile(final_re_expr)

        while True:
            match = final_re.search(html, position)
            if not match:
                # we have reached the end of the HTML string with no more elements to rewrite.
                # This shouldn't happen if we were expecting a closing tag, so warn in that case
                if until_tag:
                    warnings.warn(
                        "Reached end of string without encountering closing %r tag" % until_tag
                    )

                # either way, we can tack the remaining non-rewritten HTML on to our result,
                # and we're done
                result += html[position:]
                return mark_safe(result), len(html)
            else:
                # we've found a tag that we're interested in, but first we should add all of the
                # non-rewritten HTML up to that point on to our result
                result += html[position:match.start()]

                # once we've finished handling this tag, we'll continue from the offset after it
                position = match.end()

                # now parse the tag into its components

                tag = match.group(0)
                is_closing_tag = tag.startswith('</')

                if is_closing_tag:
                    # the regexp is structured as <(tagname)(attrs)>|</(tagname)> , so we're
                    # interested in the third group
                    tag_name = match.group(3)
                else:
                    tag_name = match.group(1)
                    attr_string = match.group(2)
                    is_self_closing = attr_string.endswith('/')
                    if is_self_closing:
                        attr_string = attr_string[:-1]

                    attrs = self.unpack_attr_string(attr_string)

                if is_closing_tag:
                    if ignored_closing_tag_count > 0:
                        # this tag is closing a tag that was previously opened in this invocation
                        # of _rewrite - it isn't the *real* closing tag
                        ignored_closing_tag_count -= 1
                    else:
                        # this is the real closing tag, so we're done with this invocation of
                        # _rewrite
                        return mark_safe(result), position

                else:
                    # this is an opening tag - look for a matching rewrite rule
                    matching_rule = None
                    for rule in self.rules_by_element[tag_name]:
                        if rule.attributes_match(attrs):
                            matching_rule = rule
                            break

                    if not matching_rule:
                        # no matching rewrite rule, so output this tag unchanged
                        result += tag

                        if tag_name == until_tag and not is_self_closing:
                            # this tag has the same name as the closing tag we're waiting for,
                            # so the next occurrence of the closing tag will be closing this one,
                            # rather than the *real* closing tag that signals the end of this
                            # invocation of _rewrite
                            ignored_closing_tag_count += 1

                    elif hasattr(matching_rule.rewriter, 'rewrite_attributes'):
                        # If the rewrite rule has a rewrite_attributes method, then we output the
                        # original tag with the updated attributes. Since the closing tag will be
                        # unchanged in the output, there's no need for us to do anything special to
                        # match it; however, if it happens to be the same as until_tag, we need to
                        # bump up ignored_closing_tag_count so that we'll skip over it rather than
                        # treating it as the *real* closing tag

                        new_attrs = matching_rule.rewriter.rewrite_attributes(tag_name, attrs)
                        new_attr_string = ' '.join(
                            '%s="%s"' % (conditional_escape(key), conditional_escape(val))
                            for key, val in new_attrs.items()
                        )
                        if is_self_closing:
                            new_tag = '<%s %s/>' % (tag_name, new_attr_string)
                        else:
                            new_tag = '<%s %s>' % (tag_name, new_attr_string)

                        result += new_tag

                        if tag_name == until_tag and not is_self_closing:
                            ignored_closing_tag_count += 1

                    elif hasattr(matching_rule.rewriter, 'rewrite_element'):
                        if is_self_closing:
                            # this element has no content, so just call rewrite_element with an
                            # empty string as content
                            rewritten_element = matching_rule.rewriter.rewrite_element(
                                tag_name, attrs, ''
                            )
                        else:
                            # we need to consume the element content by spinning up a recursive
                            # call to _rewrite and then call rewrite_element with that result
                            content, position = self._rewrite(html, start=position, until_tag=tag_name)
                            rewritten_element = matching_rule.rewriter.rewrite_element(
                                tag_name, attrs, content
                            )

                        # escape the result of rewrite_element, unless it's a safe string
                        # (e.g. the output of format_html)
                        result += conditional_escape(rewritten_element)

                    else:
                        raise Exception(
                            "Invalid ElementRewriter: %r. An ElementRewriter must implement "
                            "either rewrite_element or rewrite_attributes"
                            % matching_rule.rewriter
                        )

    @staticmethod
    def unpack_attr_string(attr_string):
        """Unpack a string of HTML attributes into a dict of unescaped strings"""
        attributes = {}
        for match in ATTRIBUTE.finditer(attr_string):
            if match.group(1):
                name = match.group(1)
                val = match.group(2)
            elif match.group(3):
                name = match.group(3)
                val = match.group(4)
            elif match.group(5):
                name = match.group(5)
                val = match.group(6)

            attributes[name] = html.unescape(val)

        return attributes


class ElementRewriter:
    pass
