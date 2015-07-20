from django.conf.urls import url

from wagtail.wagtailadmin.views import pages, page_privacy


urlpatterns = [
    url(r'^$', pages.index, name='wagtailadmin_explore_root'),
    url(r'^(\d+)/$', pages.index, name='wagtailadmin_explore'),

    url(r'^new/(\w+)/(\w+)/(\d+)/$', pages.create, name='wagtailadmin_pages_create'),
    url(r'^new/(\w+)/(\w+)/(\d+)/preview/$', pages.preview_on_create, name='wagtailadmin_pages_preview_on_create'),
    url(r'^usage/(\w+)/(\w+)/$', pages.content_type_use, name='wagtailadmin_pages_type_use'),

    url(r'^(\d+)/edit/$', pages.edit, name='wagtailadmin_pages_edit'),
    url(r'^(\d+)/edit/preview/$', pages.preview_on_edit, name='wagtailadmin_pages_preview_on_edit'),

    url(r'^preview/$', pages.preview, name='wagtailadmin_pages_preview'),
    url(r'^preview_loading/$', pages.preview_loading, name='wagtailadmin_pages_preview_loading'),

    url(r'^(\d+)/view_draft/$', pages.view_draft, name='wagtailadmin_pages_view_draft'),
    url(r'^(\d+)/add_subpage/$', pages.add_subpage, name='wagtailadmin_pages_add_subpage'),
    url(r'^(\d+)/delete/$', pages.delete, name='wagtailadmin_pages_delete'),
    url(r'^(\d+)/unpublish/$', pages.unpublish, name='wagtailadmin_pages_unpublish'),

    url(r'^search/$', pages.search, name='wagtailadmin_pages_search'),

    url(r'^(\d+)/move/$', pages.move_choose_destination, name='wagtailadmin_pages_move'),
    url(r'^(\d+)/move/(\d+)/$', pages.move_choose_destination, name='wagtailadmin_pages_move_choose_destination'),
    url(r'^(\d+)/move/(\d+)/confirm/$', pages.move_confirm, name='wagtailadmin_pages_move_confirm'),
    url(r'^(\d+)/set_position/$', pages.set_page_position, name='wagtailadmin_pages_set_page_position'),

    url(r'^(\d+)/copy/$', pages.copy, name='wagtailadmin_pages_copy'),

    url(r'^moderation/(\d+)/approve/$', pages.approve_moderation, name='wagtailadmin_pages_approve_moderation'),
    url(r'^moderation/(\d+)/reject/$', pages.reject_moderation, name='wagtailadmin_pages_reject_moderation'),
    url(r'^moderation/(\d+)/preview/$', pages.preview_for_moderation, name='wagtailadmin_pages_preview_for_moderation'),

    url(r'^(\d+)/privacy/$', page_privacy.set_privacy, name='wagtailadmin_pages_set_privacy'),

    url(r'^(\d+)/lock/$', pages.lock, name='wagtailadmin_pages_lock'),
    url(r'^(\d+)/unlock/$', pages.unlock, name='wagtailadmin_pages_unlock'),
]
