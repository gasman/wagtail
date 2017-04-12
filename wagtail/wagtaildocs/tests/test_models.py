from __future__ import absolute_import, unicode_literals

import unittest

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.files.base import ContentFile
from django.db import transaction
from django.test import TestCase, TransactionTestCase

from wagtail.wagtailcore.models import Collection, GroupCollectionPermission
from wagtail.wagtaildocs import models, signal_handlers
from wagtail.wagtaildocs.models import get_document_model
from wagtail.wagtailimages.tests.utils import get_test_image_file


class TestDocumentQuerySet(TestCase):
    def test_search_method(self):
        # Make a test document
        document = models.Document.objects.create(title="Test document")

        # Search for it
        results = models.Document.objects.search("Test")
        self.assertEqual(list(results), [document])

    def test_operators(self):
        aaa_document = models.Document.objects.create(title="AAA Test document")
        zzz_document = models.Document.objects.create(title="ZZZ Test document")

        results = models.Document.objects.search("aaa test", operator='and')
        self.assertEqual(list(results), [aaa_document])

        results = models.Document.objects.search("aaa test", operator='or')
        sorted_results = sorted(results, key=lambda doc: doc.title)
        self.assertEqual(sorted_results, [aaa_document, zzz_document])

    def test_custom_ordering(self):
        aaa_document = models.Document.objects.create(title="AAA Test document")
        zzz_document = models.Document.objects.create(title="ZZZ Test document")

        results = models.Document.objects.order_by('title').search("Test")
        self.assertEqual(list(results), [aaa_document, zzz_document])
        results = models.Document.objects.order_by('-title').search("Test")
        self.assertEqual(list(results), [zzz_document, aaa_document])


class TestDocumentPermissions(TestCase):
    def setUp(self):
        # Create some user accounts for testing permissions
        User = get_user_model()
        self.user = User.objects.create_user(username='user', email='user@email.com', password='password')
        self.owner = User.objects.create_user(username='owner', email='owner@email.com', password='password')
        self.editor = User.objects.create_user(username='editor', email='editor@email.com', password='password')
        self.editor.groups.add(Group.objects.get(name='Editors'))
        self.administrator = User.objects.create_superuser(
            username='administrator',
            email='administrator@email.com',
            password='password'
        )

        # Owner user must have the add_document permission
        self.adders_group = Group.objects.create(name='Document adders')
        GroupCollectionPermission.objects.create(
            group=self.adders_group, collection=Collection.get_first_root_node(),
            permission=Permission.objects.get(codename='add_document')
        )
        self.owner.groups.add(self.adders_group)

        # Create a document for running tests on
        self.document = models.Document.objects.create(title="Test document", uploaded_by_user=self.owner)

    def test_administrator_can_edit(self):
        self.assertTrue(self.document.is_editable_by_user(self.administrator))

    def test_editor_can_edit(self):
        self.assertTrue(self.document.is_editable_by_user(self.editor))

    def test_owner_can_edit(self):
        self.assertTrue(self.document.is_editable_by_user(self.owner))

    def test_user_cant_edit(self):
        self.assertFalse(self.document.is_editable_by_user(self.user))


class TestDocumentFilenameProperties(TestCase):
    def setUp(self):
        self.document = models.Document(title="Test document")
        self.document.file.save('example.doc', ContentFile("A boring example document"))

        self.extensionless_document = models.Document(title="Test document")
        self.extensionless_document.file.save('example', ContentFile("A boring example document"))

    def test_filename(self):
        self.assertEqual('example.doc', self.document.filename)
        self.assertEqual('example', self.extensionless_document.filename)

    def test_file_extension(self):
        self.assertEqual('doc', self.document.file_extension)
        self.assertEqual('', self.extensionless_document.file_extension)

    def tearDown(self):
        self.document.delete()
        self.extensionless_document.delete()


class TestFilesDeletedForDefaultModels(TransactionTestCase):
    '''
    Because we expect file deletion to only happen once a transaction is
    successfully committed, we must run these tests using TransactionTestCase
    per the following documentation:

        Django's TestCase class wraps each test in a transaction and rolls back that
        transaction after each test, in order to provide test isolation. This means
        that no transaction is ever actually committed, thus your on_commit()
        callbacks will never be run. If you need to test the results of an
        on_commit() callback, use a TransactionTestCase instead.
        https://docs.djangoproject.com/en/1.10/topics/db/transactions/#use-in-tests
    '''

    # indicate that these tests need the initial data loaded in migrations which
    # is not available by default for TransactionTestCase per
    # https://docs.djangoproject.com/en/1.10/topics/testing/overview/#rollback-emulation
    serialized_rollback = True

    def test_oncommit_available(self):
        self.assertEqual(hasattr(transaction, 'on_commit'), signal_handlers.TRANSACTION_ON_COMMIT_AVAILABLE)

    @unittest.skipUnless(signal_handlers.TRANSACTION_ON_COMMIT_AVAILABLE, 'is required for this test')
    def test_document_file_deleted_oncommit(self):
        with transaction.atomic():
            document = get_document_model().objects.create(title="Test Image", file=get_test_image_file())
            self.assertTrue(document.file.storage.exists(document.file.name))
            document.delete()
            self.assertTrue(document.file.storage.exists(document.file.name))
        self.assertFalse(document.file.storage.exists(document.file.name))

    @unittest.skipIf(signal_handlers.TRANSACTION_ON_COMMIT_AVAILABLE, 'duplicate')
    def test_document_file_deleted(self):
        '''
            this test duplicates `test_image_file_deleted_oncommit` for
            django 1.8 support and can be removed once django 1.8 is no longer
            supported
        '''
        with transaction.atomic():
            document = get_document_model().objects.create(title="Test Image", file=get_test_image_file())
            self.assertTrue(document.file.storage.exists(document.file.name))
            document.delete()
        self.assertFalse(document.file.storage.exists(document.file.name))
