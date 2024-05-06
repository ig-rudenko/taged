from datetime import datetime

from django.test import SimpleTestCase

from elasticsearch_control import AbstractIndex


class Index(AbstractIndex):
    str_field: str
    binary_field: str
    int_field: int
    float_field: int
    boolean_field: int
    dict_field: dict
    datetime_field: datetime

    class Meta:
        index_name = "test_index"
        settings = {}

    def json(self) -> dict:
        pass


class TestIndex(SimpleTestCase):
    def test_index(self):
        self.assertDictEqual(
            {
                "settings": {},
                "mappings": {
                    "dynamic": "true",
                    "properties": {
                        "str_field": {"type": "text"},
                        "binary_field": {"type": "text"},
                        "int_field": {"type": "integer"},
                        "float_field": {"type": "integer"},
                        "boolean_field": {"type": "integer"},
                        "dict_field": {"type": "object"},
                        "datetime_field": {"type": "date"},
                    },
                },
            },
            Index.get_index_settings(),
        )
