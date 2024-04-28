from datetime import datetime

from django.test import SimpleTestCase

from elasticsearch_control.transport import es_connector
from taged_web.repo.notes import NotesRepository, get_repository
from .fake import FakeElasticsearch


class TestRepository(SimpleTestCase):
    fake_es = None  # type: FakeElasticsearch
    repo = None  # type: NotesRepository

    @classmethod
    def setUpClass(cls):
        cls.fake_es = FakeElasticsearch()
        cls.repo = NotesRepository(cls.fake_es, "test_index", 5)

    def tearDown(self):
        self.fake_es.clear_fake_data()

    def test_repository_single_instance(self):
        """Тестируем, что функция get_repository() возвращает один и тот же экземпляр репозитория"""
        es_connector.init(self.fake_es, 5)
        self.assertIs(get_repository(), get_repository())

    def test_get_note(self):
        note = self.repo.get("1")
        self.assertEqual(note.title, "title")
        self.assertEqual(note.content, "content")
        self.assertEqual(note.tags, "tag1, tag2")
        self.assertListEqual(note.tags_list, ["tag1", "tag2"])
        self.assertEqual(note.published_at, datetime(2024, 4, 28, 0, 0, 0, 0))

    def test_add_note(self):
        note = self.repo.create("title", ["tag1", "tag2"], "content", "image")

        self.assertEqual(
            {
                "title": "title",
                "tags": ["tag1", "tag2"],
                "content": "content",
                "published_at": datetime.now(),
                "preview_image": "image",
            },
            self.fake_es.index_docs[0],
        )
        self.assertEqual(note.title, "title")
        self.assertEqual(note.content, "content")
        self.assertEqual(note.tags, "tag1, tag2")
        self.assertListEqual(note.tags_list, ["tag1", "tag2"])
        self.assertEqual(note.published_at, datetime.now())

    def test_delete_note(self):
        self.assertTrue(self.repo.delete("122"))
        self.assertEqual(self.fake_es.index_docs, [])
        self.assertEqual(self.fake_es.delete_ids, ["122"])

    def test_count_notes(self):
        self.assertEqual(self.repo.tags_count("tag1"), 123)
