from django.test import SimpleTestCase

from elasticsearch_control import QueryLimitParams
from taged_web.filters import create_notes_query_params, notes_records_filter


class TestQueryParams(SimpleTestCase):

    def test_filter_with_tags_in(self):
        query_params = create_notes_query_params("test_index", tags_in=["tag1", "tag2"], tags_off=[])
        valid_query_params = QueryLimitParams(
            index="test_index",
            source=["title", "content", "tags", "published_at", "preview_image"],
            query={"bool": {"must": [{"match": {"tags": "tag1 tag2"}}]}},
            request_timeout=5,
            sort=None,
        )
        self.assertEqual(valid_query_params, query_params)

    def test_filter_with_tags_off(self):
        query_params = create_notes_query_params("test_index", tags_in=[], tags_off=["tag1", "tag2"])
        valid_query_params = QueryLimitParams(
            index="test_index",
            source=["title", "content", "tags", "published_at", "preview_image"],
            query={"bool": {"must": [], "must_not": [{"match": {"tags": "tag1 tag2"}}]}},
            request_timeout=5,
            sort=None,
        )
        self.assertEqual(valid_query_params, query_params)

    def test_filter_with_tags_in_off(self):
        query_params = create_notes_query_params(
            "test_index", tags_in=["tag1", "tag2"], tags_off=["tag3", "tag4"]
        )
        valid_query_params = QueryLimitParams(
            index="test_index",
            source=["title", "content", "tags", "published_at", "preview_image"],
            query={
                "bool": {
                    "must": [{"match": {"tags": "tag1 tag2"}}],
                    "must_not": [{"match": {"tags": "tag3 tag4"}}],
                }
            },
            request_timeout=5,
            sort=None,
        )
        self.assertEqual(valid_query_params, query_params)

    def test_filter_with_tags_in_off_search(self):
        query_params = create_notes_query_params(
            "test_index", tags_in=["tag1", "tag2"], tags_off=["tag3", "tag4"], string="Search String"
        )
        valid_query_params = QueryLimitParams(
            index="test_index",
            source=["title", "content", "tags", "published_at", "preview_image"],
            query={
                "bool": {
                    "must": [{"match": {"tags": "tag1 tag2"}}],
                    "should": [
                        {"match": {"title": {"query": "Search String", "fuzziness": "auto"}}},
                        {"match": {"content": {"query": "Search String", "fuzziness": "auto"}}},
                    ],
                    "minimum_should_match": 1,
                    "must_not": [{"match": {"tags": "tag3 tag4"}}],
                }
            },
            request_timeout=5,
            sort=None,
        )
        self.assertEqual(valid_query_params, query_params)

    def test_filter_with_tags_in_search(self):
        query_params = create_notes_query_params(
            "test_index", tags_in=["tag1", "tag2"], string="Search String"
        )
        valid_query_params = QueryLimitParams(
            index="test_index",
            source=["title", "content", "tags", "published_at", "preview_image"],
            query={
                "bool": {
                    "must": [{"match": {"tags": "tag1 tag2"}}],
                    "should": [
                        {"match": {"title": {"query": "Search String", "fuzziness": "auto"}}},
                        {"match": {"content": {"query": "Search String", "fuzziness": "auto"}}},
                    ],
                    "minimum_should_match": 1,
                }
            },
            request_timeout=5,
            sort=None,
        )
        self.assertEqual(valid_query_params, query_params)

    def test_filter_with_tags_in_off_search_sort(self):
        query_params = create_notes_query_params(
            "test_index",
            tags_in=["tag1", "tag2"],
            tags_off=["tag3", "tag4"],
            string="Search String",
            sort="title",
        )
        valid_query_params = QueryLimitParams(
            index="test_index",
            source=["title", "content", "tags", "published_at", "preview_image"],
            query={
                "bool": {
                    "must": [{"match": {"tags": "tag1 tag2"}}],
                    "should": [
                        {"match": {"title": {"query": "Search String", "fuzziness": "auto"}}},
                        {"match": {"content": {"query": "Search String", "fuzziness": "auto"}}},
                    ],
                    "minimum_should_match": 1,
                    "must_not": [{"match": {"tags": "tag3 tag4"}}],
                }
            },
            request_timeout=5,
            sort={"title": "asc"},
        )
        self.assertEqual(valid_query_params, query_params)

    def test_filter_with_tags_in_off_search_sort_desc(self):
        query_params = create_notes_query_params(
            "test_index",
            tags_in=["tag1", "tag2"],
            tags_off=["tag3", "tag4"],
            string="Search String",
            sort="title",
            sort_desc=True,
        )
        valid_query_params = QueryLimitParams(
            index="test_index",
            source=["title", "content", "tags", "published_at", "preview_image"],
            query={
                "bool": {
                    "must": [{"match": {"tags": "tag1 tag2"}}],
                    "should": [
                        {"match": {"title": {"query": "Search String", "fuzziness": "auto"}}},
                        {"match": {"content": {"query": "Search String", "fuzziness": "auto"}}},
                    ],
                    "minimum_should_match": 1,
                    "must_not": [{"match": {"tags": "tag3 tag4"}}],
                }
            },
            request_timeout=5,
            sort={"title": "desc"},
        )
        self.assertEqual(valid_query_params, query_params)


class TestNotesFilter(SimpleTestCase):
    data = None  # type: dict

    @classmethod
    def setUpClass(cls):
        cls.data = {
            "took": 14,
            "timed_out": False,
            "_shards": {"total": 1, "successful": 1, "skipped": 0, "failed": 0},
            "hits": {
                "total": {"value": 2, "relation": "eq"},
                "max_score": 1.5211289,
                "hits": [
                    {
                        "_index": "company",
                        "_type": "_doc",
                        "_id": "eb1e362a-b7b2-4c2e-84e3-717caa690117",
                        "_score": 1.5211289,
                        "_ignored": ["content.keyword"],
                        "_source": {
                            "preview_image": "https://static.1cloud.ru/img/blog/516.png",
                            "title": "Docker",
                            "published_at": "2024-02-12T23:55:49.636165",
                            "tags": ["Docker"],
                        },
                    },
                    {
                        "_index": "company",
                        "_type": "_doc",
                        "_id": "de42f4d4-cb7e-4e63-9ad1-3cdfc08684d5",
                        "_score": 0.4218049,
                        "_ignored": ["content.keyword"],
                        "_source": {
                            "preview_image": "https://static.1cloud.ru/img/blog/552.png",
                            "title": "Ansible",
                            "published_at": "2024-02-12T23:41:49.136742",
                            "tags": ["Ansible", "IaC"],
                        },
                    },
                ],
            },
        }
        cls.note_docker = {
            "id": "eb1e362a-b7b2-4c2e-84e3-717caa690117",
            "title": "Docker",
            "tags": ["Docker"],
            "published_at": "2024-02-12T23:55:49.636165",
            "content": None,
            "preview_image": "https://static.1cloud.ru/img/blog/516.png",
            "score": 1.0,
        }
        cls.note_ansible = {
            "id": "de42f4d4-cb7e-4e63-9ad1-3cdfc08684d5",
            "title": "Ansible",
            "tags": ["Ansible", "IaC"],
            "published_at": "2024-02-12T23:41:49.136742",
            "content": None,
            "preview_image": "https://static.1cloud.ru/img/blog/552.png",
            "score": 0.277,
        }

    def test_notes_filter(self):
        self.assertListEqual(
            [self.note_docker], notes_records_filter(self.data, tags_in=["Docker"], tags_off=[])
        )
        self.assertListEqual(
            [self.note_ansible], notes_records_filter(self.data, tags_in=[], tags_off=["Docker"])
        )
        self.assertListEqual([], notes_records_filter(self.data, tags_in=["Docker"], tags_off=["Docker"]))
        self.assertListEqual([], notes_records_filter(self.data, tags_in=["Ansible"], tags_off=["IaC"]))
        self.assertListEqual(
            [self.note_docker, self.note_ansible], notes_records_filter(self.data, tags_in=[], tags_off=[])
        )
