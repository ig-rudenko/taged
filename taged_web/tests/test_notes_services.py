from datetime import datetime

from django.http import Http404
from django.test import TestCase

from elasticsearch_control.transport import es_connector
from .fake import FakeElasticsearch
from ..models import User, Tags
from ..services.notes import get_note_or_404


class TestNotesServices(TestCase):
    fake_es = None  # type: FakeElasticsearch

    @classmethod
    def setUpTestData(cls):
        cls.fake_es = FakeElasticsearch()
        es_connector.init(cls.fake_es, 5)

    def setUp(self):
        self.user = User.objects.create_user("TestNotesServices", "<EMAIL>", "<PASSWORD>")
        self.tag1 = Tags.objects.create(tag_name="tag1")
        self.tag2 = Tags.objects.create(tag_name="tag2")

    def test_get_note_or_404(self):
        self.user.tags_set.add(self.tag1, self.tag2)

        note = get_note_or_404("1", self.user)
        self.assertDictEqual(
            {
                "title": "title",
                "tags": ["tag1", "tag2"],
                "published_at": datetime(2024, 4, 28, 0, 0),
                "content": "content",
                "preview_image": "//image.png",
            },
            note.json(),
        )

    def test_get_note_or_404_not_found(self):
        """Запись не найдена"""
        with self.assertRaises(Http404):
            get_note_or_404("", self.user)

    def test_get_note_or_404_user_no_access(self):
        """У пользователя нет доступа к тегам записи"""
        with self.assertRaises(Http404):
            get_note_or_404("1", self.user)
