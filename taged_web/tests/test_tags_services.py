from django.test import TestCase

from taged_web.models import User, Tags
from taged_web.services.tags import add_tags_to_user_if_not_exist, get_available_tags, get_unavailable_tags


class TestAddTagsToUser(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("TestAddTagsToUser", "<EMAIL>", "<PASSWORD>")

    def test_add_tags_to_user_if_not_exist(self):
        self.assertEqual(Tags.objects.count(), 0)

        add_tags_to_user_if_not_exist(["tag1", "tag2", "tag3"], self.user)
        self.assertEqual(Tags.objects.count(), 3)
        self.assertEqual(self.user.tags_set.count(), 3)

    def test_add_tags_to_user_if_not_exist_no_duplicate(self):
        self.assertEqual(Tags.objects.count(), 0)

        add_tags_to_user_if_not_exist(["tag1", "tag2", "tag3"], self.user)
        self.assertEqual(Tags.objects.count(), 3)
        self.assertEqual(self.user.tags_set.count(), 3)

        add_tags_to_user_if_not_exist(["tag1", "tag2", "tag3"], self.user)
        self.assertEqual(Tags.objects.count(), 3)
        self.assertEqual(self.user.tags_set.count(), 3)

    def test_add_tags_to_user_if_not_exist_with_user_tags(self):
        self.user.tags_set.add(Tags.objects.create(tag_name="tag1"))

        add_tags_to_user_if_not_exist(["tag1", "tag2", "tag3"], self.user)
        self.assertEqual(Tags.objects.count(), 3)
        self.assertEqual(self.user.tags_set.count(), 3)


class TestAvailableUnavailableTags(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("TestAddTagsToUser", "<EMAIL>", "<PASSWORD>")
        self.user.tags_set.add(Tags.objects.create(tag_name="tag1"))
        self.user.tags_set.add(Tags.objects.create(tag_name="tag2"))
        self.user.tags_set.add(Tags.objects.create(tag_name="tag3"))
        Tags.objects.create(tag_name="tag4")
        Tags.objects.create(tag_name="tag5")

    def test_get_available_tags(self):
        self.assertEqual(
            ["tag1", "tag2", "tag3", "tag4", "tag5"],
            list(Tags.objects.all().values_list("tag_name", flat=True)),
        )
        self.assertSetEqual({"tag1", "tag2", "tag3"}, set(get_available_tags(self.user)))

    def test_get_unavailable_tags(self):
        self.assertEqual(
            ["tag1", "tag2", "tag3", "tag4", "tag5"],
            list(Tags.objects.all().values_list("tag_name", flat=True)),
        )
        self.assertSetEqual({"tag4", "tag5"}, set(get_unavailable_tags(self.user)))
