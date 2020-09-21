import json

from django.core.management.base import BaseCommand
from wagtail.core.models import PageLogEntry, PageRevision


def get_comparison(page, revision_a, revision_b):
    comparison = page.get_edit_handler().get_comparison()
    comparison = [comp(revision_a, revision_b) for comp in comparison]
    comparison = [comp for comp in comparison if comp.has_changed()]

    return comparison


class Command(BaseCommand):
    def handle(self, *args, **options):
        current_page_id = None
        missing_models_content_type_ids = set()
        for revision in PageRevision.objects.order_by('page_id', 'created_at').select_related('page').iterator():
            # This revision is for a page type that is no longer in the database. Bail out early.
            if revision.page.content_type_id in missing_models_content_type_ids:
                continue
            if not revision.page.specific_class:
                missing_models_content_type_ids.add(revision.page.content_type_id)
                continue

            is_new_page = revision.page_id != current_page_id
            if is_new_page:
                # reset previous revision when encountering a new page.
                previous_revision = None
                previous_revision_content = None

            has_content_changes = False
            current_page_id = revision.page_id
            current_revision_content = json.loads(revision.content_json)
            current_revision_live_revision = current_revision_content.get('live_revision')

            # Discard metadata fields that are not related to content edits, as these may
            # produce false positives when checking for changes
            for field in [
                'path', 'depth', 'numchild', 'url_path', 'draft_title', 'live',
                'has_unpublished_changes', 'owner', 'locked', 'locked_at', 'locked_by',
                'expired', 'first_published_at', 'last_published_at',
                'latest_revision_created_at', 'live_revision',
            ]:
                current_revision_content.pop(field, None)

            if not PageLogEntry.objects.filter(revision=revision).exists():
                published = revision.id == revision.page.live_revision_id

                if previous_revision is not None:
                    if current_revision_live_revision == previous_revision.id:
                        # Log the previous revision publishing.
                        self.log_page_action('wagtail.publish', previous_revision, True)

                    print("revision %d: %s" % (revision.id, json.dumps(current_revision_content)))

                    has_content_changes = (current_revision_content != previous_revision_content)

                if is_new_page or has_content_changes or published:
                    if is_new_page:
                        action = 'wagtail.create'
                    elif published:
                        action = 'wagtail.publish'
                    else:
                        action = 'wagtail.edit'

                    if published and has_content_changes:
                        # When publishing, also log the 'draft save', but only if there have been content changes
                        self.log_page_action('wagtail.edit', revision, has_content_changes)

                    self.log_page_action(action, revision, has_content_changes)

            previous_revision = revision
            previous_revision_content = current_revision_content

    def log_page_action(self, action, revision, has_content_changes):
        PageLogEntry.objects.log_action(
            instance=revision.page.specific,
            action=action,
            data='',
            revision=None if action == 'wagtail.create' else revision,
            user=revision.user,
            timestamp=revision.created_at,
            content_changed=has_content_changes,
        )
