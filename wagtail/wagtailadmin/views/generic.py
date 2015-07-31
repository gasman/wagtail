from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import ugettext_lazy, ugettext as _
from django.views.generic.base import View

# Must be imported from Django so we get the new implementation of with_metaclass
from django.utils import six

from wagtail.wagtailadmin import messages


class PermissionCheckedView(View):
    def dispatch(self, request, *args, **kwargs):
        if getattr(self, 'permission_required', None) is not None:
            if not request.user.has_perm(self.permission_required):
                messages.error(request, _('Sorry, you do not have permission to access this area.'))
                return redirect('wagtailadmin_home')

        return super(PermissionCheckedView, self).dispatch(request, *args, **kwargs)


class ModelPermissionMetaclass(type):
    """
    Populates the attributes 'add_permission_name', 'change_permission_name' and 'delete_permission_name'
    with sensible defaults based on the 'model' attribute (if one is defined).
    """
    def __new__(mcs, name, bases, attrs):
        new_class = (super(ModelPermissionMetaclass, mcs).__new__(mcs, name, bases, attrs))
        if hasattr(new_class, 'model'):
            app_label = new_class.model._meta.app_label
            model_name = new_class.model._meta.model_name

            if not hasattr(new_class, 'add_permission_name'):
                new_class.add_permission_name = "%s.add_%s" % (app_label, model_name)
            if not hasattr(new_class, 'change_permission_name'):
                new_class.change_permission_name = "%s.change_%s" % (app_label, model_name)
            if not hasattr(new_class, 'delete_permission_name'):
                new_class.delete_permission_name = "%s.delete_%s" % (app_label, model_name)

        return new_class


class ModelAdminUrlMetaclass(type):
    """
    Populates the attributes 'index_url_name', 'add_url_name', 'edit_url_name' and 'delete_url_name'
    with sensible defaults based on the 'url_namespace' attribute (if one is defined).
    """
    def __new__(mcs, name, bases, attrs):
        new_class = (super(ModelAdminUrlMetaclass, mcs).__new__(mcs, name, bases, attrs))
        if hasattr(new_class, 'url_namespace'):
            if not hasattr(new_class, 'index_url_name'):
                new_class.index_url_name = "%s:index" % new_class.url_namespace
            if not hasattr(new_class, 'add_url_name'):
                new_class.add_url_name = "%s:add" % new_class.url_namespace
            if not hasattr(new_class, 'edit_url_name'):
                new_class.edit_url_name = "%s:edit" % new_class.url_namespace
            if not hasattr(new_class, 'delete_url_name'):
                new_class.delete_url_name = "%s:delete" % new_class.url_namespace

        return new_class


class IndexViewMetaclass(ModelPermissionMetaclass, ModelAdminUrlMetaclass):
    def __new__(mcs, name, bases, attrs):
        new_class = (super(IndexViewMetaclass, mcs).__new__(mcs, name, bases, attrs))

        # if a subclass of IndexView does not specify its own 'permission_required' attribute,
        # set it to the same as change_permission_name
        if not hasattr(new_class, 'permission_required') and hasattr(new_class, 'change_permission_name'):
            new_class.permission_required = new_class.change_permission_name

        return new_class


class IndexView(six.with_metaclass(IndexViewMetaclass, PermissionCheckedView)):
    def get_queryset(self):
        self.ordering = self.request.GET.get('ordering', self.default_order)
        return self.model.objects.order_by(self.ordering)

    def get(self, request):
        object_list = self.get_queryset()

        return render(request, self.template, {
            'view': self,
            'can_add': request.user.has_perm(self.add_permission_name),
            'ordering': self.ordering,
            self.context_object_name: object_list,
        })


class CreateViewMetaclass(ModelPermissionMetaclass, ModelAdminUrlMetaclass):
    def __new__(mcs, name, bases, attrs):
        new_class = (super(CreateViewMetaclass, mcs).__new__(mcs, name, bases, attrs))

        # if a subclass of CreateView does not specify its own 'permission_required' attribute,
        # set it to the same as add_permission_name
        if not hasattr(new_class, 'permission_required') and hasattr(new_class, 'add_permission_name'):
            new_class.permission_required = new_class.add_permission_name

        return new_class


class CreateView(six.with_metaclass(CreateViewMetaclass, PermissionCheckedView)):
    template = 'wagtailadmin/generic/create.html'
    form_template = 'wagtailadmin/generic/_form.html'

    def get_success_message(self, instance):
        return self.success_message.format(instance)

    def get_error_message(self):
        return self.error_message

    def get(self, request):
        self.form = self.form_class()
        return self.render_to_response()

    def post(self, request):
        self.form = self.form_class(request.POST)
        if self.form.is_valid():
            instance = self.form.save()
            messages.success(request, self.get_success_message(instance), buttons=[
                messages.button(reverse(self.edit_url_name, args=(instance.id,)), _('Edit'))
            ])
            return redirect(self.index_url_name)
        else:
            messages.error(request, self.get_error_message())
            return self.render_to_response()

    def render_to_response(self):
        return render(self.request, self.template, {
            'view': self,
            'form': self.form,
        })


class EditViewMetaclass(ModelPermissionMetaclass, ModelAdminUrlMetaclass):
    def __new__(mcs, name, bases, attrs):
        new_class = (super(EditViewMetaclass, mcs).__new__(mcs, name, bases, attrs))

        # if a subclass of EditView does not specify its own 'permission_required' attribute,
        # set it to the same as change_permission_name
        if not hasattr(new_class, 'permission_required') and hasattr(new_class, 'change_permission_name'):
            new_class.permission_required = new_class.change_permission_name

        return new_class


class EditView(six.with_metaclass(EditViewMetaclass, PermissionCheckedView)):
    template = 'wagtailadmin/generic/edit.html'
    form_template = 'wagtailadmin/generic/_form.html'

    page_title = ugettext_lazy("Editing")

    def get_page_subtitle(self):
        return str(self.instance)

    def get_success_message(self, instance):
        return self.success_message.format(instance)

    def get_error_message(self):
        return self.error_message

    def get_edit_url(self):
        return reverse(self.edit_url_name, args=(self.instance.id,))

    def get_delete_url(self):
        return reverse(self.delete_url_name, args=(self.instance.id,))

    def get(self, request, instance_id):
        self.instance = get_object_or_404(self.model, id=instance_id)
        self.form = self.form_class(instance=self.instance)
        return self.render_to_response()

    def post(self, request, instance_id):
        self.instance = get_object_or_404(self.model, id=instance_id)

        self.form = self.form_class(request.POST, instance=self.instance)
        if self.form.is_valid():
            self.form.save()
            messages.success(request, self.get_success_message(self.instance), buttons=[
                messages.button(self.get_edit_url(), _('Edit'))
            ])
            return redirect(self.index_url_name)
        else:
            messages.error(request, self.get_error_message())
            return self.render_to_response()

    def render_to_response(self):
        return render(self.request, self.template, {
            'view': self,
            self.context_object_name: self.instance,
            'form': self.form,
            'can_delete': self.request.user.has_perm(self.delete_permission_name),
        })


class DeleteViewMetaclass(ModelPermissionMetaclass, ModelAdminUrlMetaclass):
    def __new__(mcs, name, bases, attrs):
        new_class = (super(DeleteViewMetaclass, mcs).__new__(mcs, name, bases, attrs))

        # if a subclass of DeleteView does not specify its own 'permission_required' attribute,
        # set it to the same as delete_permission_name
        if not hasattr(new_class, 'permission_required') and hasattr(new_class, 'delete_permission_name'):
            new_class.permission_required = new_class.delete_permission_name

        return new_class


class DeleteView(six.with_metaclass(DeleteViewMetaclass, PermissionCheckedView)):
    template = 'wagtailadmin/generic/confirm_delete.html'

    def get_page_subtitle(self):
        return str(self.instance)

    def get_success_message(self, instance):
        return self.success_message.format(instance)

    def get_delete_url(self):
        return reverse(self.delete_url_name, args=(self.instance.id,))

    def get(self, request, instance_id):
        self.instance = get_object_or_404(self.model, id=instance_id)
        return render(request, self.template, {
            'view': self,
            self.context_object_name: self.instance,
        })

    def post(self, request, instance_id):
        self.instance = get_object_or_404(self.model, id=instance_id)

        self.instance.delete()
        messages.success(request, self.get_success_message(self.instance))
        return redirect(self.index_url_name)
