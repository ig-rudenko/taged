from uuid import uuid4

from django.core.cache import cache
from django.shortcuts import reverse
from django.test import TestCase
from rest_framework.test import APIClient

from taged_web.models import User


class TestEditors(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.register_url = reverse("api-notes:register-note-editor")
        cls.user = User.objects.create_user("user", "user@example.com", "user")
        cls.superuser = User.objects.create_superuser("admin", "admin@admin.com", "admin")

    def setUp(self):
        self.client = APIClient()

    def tearDown(self):
        cache.clear()

    def test_anonymous_user(self):
        data = {
            "note": uuid4().hex,
            "editor": uuid4().hex,
        }
        resp = self.client.post(self.register_url, data)
        self.assertEqual(resp.status_code, 401)

    def test_register_by_user(self):
        data = {
            "note": uuid4().hex,
            "editor": uuid4().hex,
        }

        self.client.force_login(self.user)
        resp = self.client.post(self.register_url, data)
        self.assertEqual(resp.status_code, 201)

    def test_register_by_superuser(self):
        data = {
            "note": uuid4().hex,
            "editor": uuid4().hex,
        }

        self.client.force_login(self.superuser)
        resp = self.client.post(self.register_url, data)
        self.assertEqual(resp.status_code, 201)

    def test_two_register_one_note_one_user(self):
        note_id = uuid4().hex
        editor1 = uuid4().hex
        editor2 = uuid4().hex

        data1 = {
            "note": note_id,
            "editor": editor1,
        }
        data2 = {
            "note": note_id,
            "editor": editor2,
        }

        check_url = reverse("api-notes:get-note-editors", args=[note_id])

        self.client.force_login(self.user)
        self.client.post(self.register_url, data1)
        self.client.post(self.register_url, data2)

        resp = self.client.get(check_url)

        self.assertListEqual(resp.data, [editor1, editor2])

    def test_two_register_change_note(self):
        note_id_1 = uuid4().hex
        note_id_2 = uuid4().hex
        editor1 = uuid4().hex
        editor2 = uuid4().hex

        data1 = {
            "note": note_id_1,
            "editor": editor1,
        }
        data2 = {
            "note": note_id_1,
            "editor": editor2,
        }
        data3 = {
            "note": note_id_2,
            "editor": editor2,
        }

        self.client.force_login(self.user)
        self.client.post(self.register_url, data1)  # Editor 1 - note 1
        self.client.post(self.register_url, data2)  # Editor 2 - note 1
        self.client.post(self.register_url, data3)  # Editor 2 - note 2

        # Проверяем редакторов первой заметки
        check_url_1 = reverse("api-notes:get-note-editors", args=[note_id_1])
        resp = self.client.get(check_url_1)
        self.assertListEqual(resp.data, [editor1], "Первую заметку редактирует только первый редактор")

        # Проверяем редакторов второй заметки
        check_url_2 = reverse("api-notes:get-note-editors", args=[note_id_2])
        resp = self.client.get(check_url_2)
        self.assertListEqual(resp.data, [editor2], "Вторую заметку редактирует только второй редактор")
