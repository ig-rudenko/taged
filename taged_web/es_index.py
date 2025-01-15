import os
import re
from datetime import datetime
from typing import Literal, NamedTuple

from elasticsearch_control import AbstractIndex

T_Values = Literal["title", "content", "tags", "published_at", "preview_image"]


class PostFile(NamedTuple):
    name: str
    size: int

    def json(self):
        return {
            "name": self.name,
            "size": self.size,
        }


class PostIndex(AbstractIndex):
    title: str
    content: str
    tags: str
    published_at: datetime
    preview_image: str

    class Meta:
        index_name = os.getenv("NOTE_INDEX_NAME", "notes")
        settings = {
            "analysis": {
                "filter": {
                    "ru_stop": {"type": "stop", "stopwords": "_russian_"},
                    "ru_stemmer": {"type": "stemmer", "language": "russian"},
                },
                "analyzer": {
                    "default": {
                        "char_filter": ["html_strip"],
                        "tokenizer": "standard",
                        "filter": ["lowercase", "ru_stop", "ru_stemmer"],
                    },
                    "without_stemming": {
                        "tokenizer": "standard",
                        "filter": ["lowercase", "ru_stop"],
                    },
                },
            }
        }
        mappings = {
            "embedding": {"type": "dense_vector", "dims": 312},
        }

    @staticmethod
    def get_first_image_url(content: str) -> str:
        first_image = re.search(r'<img .*?src="(\S+)"', content)
        if first_image:
            return first_image.group(1)
        return ""

    @property
    def tags_list(self) -> list[str]:
        if isinstance(self.tags, str):
            return self.tags.split(", ")
        if isinstance(self.tags, list):
            return self.tags

    def json(self) -> dict:
        return {
            "title": self.title,
            "tags": self.tags_list,
            "published_at": self.published_at,
            "content": self.content,
            "preview_image": self.preview_image,
        }
