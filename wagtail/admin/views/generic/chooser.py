from django import forms
from django.contrib.admin.utils import unquote
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.forms.models import modelform_factory
from django.http import Http404
from django.template.loader import render_to_string
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic.base import ContextMixin, View

from wagtail.admin.admin_url_finder import AdminURLFinder
from wagtail.admin.modal_workflow import render_modal_workflow
from wagtail.admin.ui.tables import Table, TitleColumn
from wagtail.search.backends import get_search_backend
from wagtail.search.index import class_is_indexed


class ModalPageFurnitureMixin(ContextMixin):
    """
    Add icon, page title and page subtitle to the template context
    """

    icon = None
    page_title = None
    page_subtitle = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "header_icon": self.icon,
                "page_title": self.page_title,
                "page_subtitle": self.page_subtitle,
            }
        )
        return context


class BaseChooseView(ModalPageFurnitureMixin, ContextMixin, View):
    """
    Provides common functionality for views that present a (possibly searchable / filterable) list
    of objects to choose from
    """

    model = None
    per_page = 10
    chosen_url_name = None
    results_url_name = None
    icon = "snippet"
    page_title = _("Choose")
    filter_form_class = None
    template_name = "wagtailadmin/generic/chooser/chooser.html"
    results_template_name = "wagtailadmin/generic/chooser/results.html"

    def get_object_list(self):
        objects = self.model.objects.all()

        # Preserve the model-level ordering if specified, but fall back on PK if not
        # (to ensure pagination is consistent)
        if not objects.ordered:
            objects = objects.order_by("pk")

        return objects

    def get_filter_form_class(self):
        if self.filter_form_class:
            return self.filter_form_class
        else:
            fields = {}
            if class_is_indexed(self.model):
                fields["q"] = forms.CharField(
                    label=_("Search term"), widget=forms.TextInput(), required=False
                )

            return type(
                "FilterForm",
                (forms.Form,),
                fields,
            )

    def get_filter_form(self):
        FilterForm = self.get_filter_form_class()
        return FilterForm(self.request.GET)

    def filter_object_list(self, objects, form):
        search_query = form.cleaned_data.get("q")
        if search_query:
            search_backend = get_search_backend()
            objects = search_backend.search(search_query, objects)
            self.is_searching = True
            self.search_query = search_query
        return objects

    def get_results_url(self):
        return reverse(self.results_url_name)

    @property
    def columns(self):
        return [
            TitleColumn(
                "title",
                label=_("Title"),
                accessor=str,
                url_name=self.chosen_url_name,
                link_attrs={"data-chooser-modal-choice": True},
            ),
        ]

    def get(self, request):
        objects = self.get_object_list()
        self.is_searching = False
        self.search_query = None

        self.filter_form = self.get_filter_form()
        if self.filter_form.is_valid():
            objects = self.filter_object_list(objects, self.filter_form)

        paginator = Paginator(objects, per_page=self.per_page)
        self.results = paginator.get_page(request.GET.get("p"))
        self.table = Table(self.columns, self.results)

        return self.render_to_response()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "results": self.results,
                "table": self.table,
                "results_url": self.get_results_url(),
                "is_searching": self.is_searching,
                "search_query": self.search_query,
            }
        )
        return context

    def render_to_response(self):
        raise NotImplementedError()


class CreationFormMixin:
    """
    Provides a form class for creating new objects
    """

    creation_form_class = None
    form_fields = None
    exclude_form_fields = None
    creation_form_template_name = "wagtailadmin/generic/chooser/creation_form.html"
    create_action_label = _("Create")
    create_action_clicked_label = None

    def get_creation_form_class(self):
        if self.creation_form_class:
            return self.creation_form_class
        elif self.form_fields is not None or self.exclude_form_fields is not None:
            return modelform_factory(
                self.model, fields=self.form_fields, exclude=self.exclude_form_fields
            )

    def get_creation_form_context_data(self):
        # don't include the actual form object here, as different views will instantiate it
        # differently (e.g. unbound for the initial GET, bound for a POST)
        return {
            "create_action_label": self.create_action_label,
            "create_action_clicked_label": self.create_action_clicked_label,
        }


class ChooseViewMixin(CreationFormMixin):
    """
    A view that renders a complete modal response for the chooser, including a tab for the object
    listing and (optionally) a 'create' form
    """

    search_tab_label = _("Search")
    creation_tab_label = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_creation_form_context_data())
        context.update(
            {
                "filter_form": self.filter_form,
                "search_tab_label": self.search_tab_label,
                "creation_tab_label": self.creation_tab_label
                or self.create_action_label,
            }
        )

        creation_form_class = self.get_creation_form_class()
        if creation_form_class:
            context["creation_form"] = creation_form_class()

        return context

    # Return the choose view as a ModalWorkflow response
    def render_to_response(self):
        return render_modal_workflow(
            self.request,
            self.template_name,
            None,
            self.get_context_data(),
            json_data={
                "step": "choose",
            },
        )


class ChooseView(ChooseViewMixin, BaseChooseView):
    pass


class ChooseResultsViewMixin:
    """
    A view that renders just the object listing as an HTML fragment, used to replace the listing
    when paginating or searching
    """

    # Return just the HTML fragment for the results
    def render_to_response(self):
        return TemplateResponse(
            self.request,
            self.results_template_name,
            self.get_context_data(),
        )


class ChooseResultsView(ChooseResultsViewMixin, BaseChooseView):
    pass


class ChosenResponseMixin:
    """
    Provides methods for returning the chosen object from the modal workflow.
    """

    response_data_title_key = "title"

    def get_object_id(self, instance):
        return instance.pk

    def get_display_title(self, instance):
        """
        Return a string representation of the given object instance
        """
        return str(instance)

    def get_edit_item_url(self, instance):
        return AdminURLFinder(user=self.request.user).get_edit_url(instance)

    def get_chosen_response_data(self, item):
        """
        Generate the result value to be returned when an object has been chosen
        """
        return {
            "id": str(self.get_object_id(item)),
            self.response_data_title_key: self.get_display_title(item),
            "edit_link": self.get_edit_item_url(item),
        }

    def get_chosen_response(self, item):
        """
        Return the HTTP response to indicate that an object has been chosen
        """
        response_data = self.get_chosen_response_data(item)

        return render_modal_workflow(
            self.request,
            None,
            None,
            None,
            json_data={"step": "chosen", "result": response_data},
        )


class ChosenView(ChosenResponseMixin, View):
    """
    A view that takes an object ID in the URL and returns a modal workflow response indicating
    that object has been chosen
    """

    model = None

    def get_object(self, pk):
        return self.model.objects.get(pk=pk)

    def get(self, request, pk):
        try:
            item = self.get_object(unquote(pk))
        except ObjectDoesNotExist:
            raise Http404

        return self.get_chosen_response(item)


class CreateView(CreationFormMixin, ChosenResponseMixin, View):
    """
    A view that handles submissions of the 'create' form
    """

    model = None

    def get(self, request):
        form_class = self.get_creation_form_class()
        self.form = form_class()
        return self.render_reshow_creation_form_response()

    def render_reshow_creation_form_response(self):
        context = {
            "creation_form": self.form,
        }
        context.update(self.get_creation_form_context_data())
        response_html = render_to_string(
            self.creation_form_template_name, context, self.request
        )
        return render_modal_workflow(
            self.request,
            None,
            None,
            None,
            json_data={
                "step": "reshow_creation_form",
                "htmlFragment": response_html,
            },
        )
