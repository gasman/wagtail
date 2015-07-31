from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import ugettext as _
from django.views.generic.base import View

from wagtail.wagtailadmin import messages


class PermissionCheckedView(View):
    permission_name = None

    def dispatch(self, request, *args, **kwargs):
        if self.permission_name is not None:
            if not request.user.has_perm(self.permission_name):
                messages.error(request, _('Sorry, you do not have permission to access this area.'))
                return redirect('wagtailadmin_home')

        return super(PermissionCheckedView, self).dispatch(request, *args, **kwargs)


class IndexView(PermissionCheckedView):
    def get_queryset(self):
        return self.model.objects.order_by(self.default_order)

    def get(self, request):
        object_list = self.get_queryset()

        return render(request, self.template, {
            'view': self,
            'can_add': request.user.has_perm(self.add_permission_name),
            self.context_object_name: object_list,
        })


class CreateView(PermissionCheckedView):
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
            'form': self.form,
        })


class EditView(PermissionCheckedView):
    def get_success_message(self, instance):
        return self.success_message.format(instance)

    def get_error_message(self):
        return self.error_message

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
                messages.button(reverse(self.edit_url_name, args=(self.instance.id,)), _('Edit'))
            ])
            return redirect(self.index_url_name)
        else:
            messages.error(request, self.get_error_message())
            return self.render_to_response()

    def render_to_response(self):
        return render(self.request, self.template, {
            self.context_object_name: self.instance,
            'form': self.form,
        })


class DeleteView(PermissionCheckedView):
    def get_success_message(self, instance):
        return self.success_message.format(instance)

    def get(self, request, instance_id):
        instance = get_object_or_404(self.model, id=instance_id)
        return render(request, self.template, {
            self.context_object_name: instance,
        })

    def post(self, request, instance_id):
        instance = get_object_or_404(self.model, id=instance_id)

        instance.delete()
        messages.success(request, self.get_success_message(instance))
        return redirect(self.index_url_name)
