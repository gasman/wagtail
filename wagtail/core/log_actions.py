try:
    from asgiref.local import Local
except ImportError:  # fallback for Django <3.0
    from threading import local as Local

from django.utils.translation import gettext_lazy as _

from wagtail.core import hooks


_active = Local()


class LogContext:
    """
    Stores data about the environment in which a logged action happens -
    e.g. the active user - to be stored in the log entry for that action.
    """
    def __init__(self, user=None):
        self.user = user

    def __enter__(self):
        self._old_log_context = getattr(_active, 'value', None)
        activate(self)
        return self

    def __exit__(self, type, value, traceback):
        if self._old_log_context:
            activate(self._old_log_context)
        else:
            deactivate()


empty_log_context = LogContext()


def activate(log_context):
    _active.value = log_context


def deactivate():
    del _active.value


def get_active_log_context():
    return getattr(_active, 'value', empty_log_context)


class NullAdminURLFinder:
    """
    An admin url finder takes the current user as an argument to its constructor, and
    provides a `get_edit_url` method that accepts a log entry and returns the URL to the
    admin view for editing the logged item, or None if no URL exists or the user lacks
    permission for it. Where possible, database lookups for the permission check should
    be done up-front in the constructor, so that multiple calls to get_edit_url can be
    performed without repeated queries.

    This is the null admin URL finder used when no edit URL exists; get_edit_url always
    returns None.
    """
    def __init__(self, user):
        pass

    def get_edit_url(self, log_entry):
        return None


class LogActionRegistry:
    """
    A central store for log actions.
    The expected format for registered log actions: Namespaced action, Action label, Action message (or callable)
    """
    def __init__(self):
        # Has the register_log_actions hook been run for this registry?
        self.has_scanned_for_actions = False

        # Holds the actions.
        self.actions = {}

        # Holds a list of action, action label tuples for use in filters
        self.choices = []

        # Holds the action messages, keyed by action
        self.messages = {}

        # Holds the comments, keyed by action
        self.comments = {}

        # Tracks which LogEntry model should be used for a given object class
        self.log_entry_models_by_model = {}

        # All distinct log entry models registered with register_model
        self.log_entry_models = set()

        # Tracks which admin url finder class should be used for a given object class.
        self.admin_url_finders_by_model = {}

    def scan_for_actions(self):
        if not self.has_scanned_for_actions:
            for fn in hooks.get_hooks('register_log_actions'):
                fn(self)

            self.has_scanned_for_actions = True

        return self.actions

    def get_actions(self):
        return self.scan_for_actions()

    def register_model(self, cls, log_entry_model):
        self.log_entry_models_by_model[cls] = log_entry_model
        self.log_entry_models.add(log_entry_model)

    def register_action(self, action, label, message, comment=None):
        self.actions[action] = (label, message)
        self.messages[action] = message
        if comment:
            self.comments[action] = comment
        self.choices.append((action, label))

    def register_admin_url_finder(self, model, finder):
        self.admin_url_finders_by_model[model] = finder

    def get_choices(self):
        self.scan_for_actions()
        return self.choices

    def get_messages(self):
        self.scan_for_actions()
        return self.messages

    def get_comments(self):
        self.scan_for_actions()
        return self.comments

    def get_log_entry_models(self):
        self.scan_for_actions()
        return self.log_entry_models

    def format_message(self, log_entry):
        message = self.get_messages().get(log_entry.action, _('Unknown %(action)s') % {'action': log_entry.action})
        if callable(message):
            if getattr(message, 'takes_log_entry', False):
                message = message(log_entry)
            else:
                # Pre Wagtail 2.14, we only passed the data into the message generator
                message = message(log_entry.data)

        return message

    def format_comment(self, log_entry):
        message = self.get_comments().get(log_entry.action, '')
        if callable(message):
            if getattr(message, 'takes_log_entry', False):
                message = message(log_entry)
            else:
                # Pre Wagtail 2.14, we only passed the data into the message generator
                message = message(log_entry.data)

        return message

    def get_action_label(self, action):
        return self.get_actions()[action][0]

    def get_log_model_for_model(self, model):
        self.scan_for_actions()

        for cls in model.__mro__:
            log_entry_model = self.log_entry_models_by_model.get(cls)
            if log_entry_model:
                return log_entry_model

    def get_log_model_for_instance(self, instance):
        return self.get_log_model_for_model(type(instance))

    def get_admin_url_finder(self, model, user):
        self.scan_for_actions()

        for cls in model.__mro__:
            finder = self.admin_url_finders_by_model.get(cls)
            if finder:
                return finder(user)

        return NullAdminURLFinder(user)

    def log(self, instance, action, user=None, **kwargs):
        self.scan_for_actions()

        # find the log entry model for the given object type
        log_entry_model = self.get_log_model_for_instance(instance)
        if log_entry_model is None:
            # no logger registered for this object type - silently bail
            return

        user = user or get_active_log_context().user
        return log_entry_model.objects.log_action(instance, action, user=user, **kwargs)

    def get_logs_for_instance(self, instance):
        log_entry_model = self.get_log_model_for_instance(instance)
        if log_entry_model is None:
            # this model has no logs; return an empty queryset of the basic log model
            from wagtail.core.models import ModelLogEntry
            return ModelLogEntry.objects.none()

        return log_entry_model.objects.for_instance(instance)


registry = LogActionRegistry()


def log(instance, action, **kwargs):
    return registry.log(instance, action, **kwargs)
