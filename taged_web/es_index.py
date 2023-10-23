import shutil
from datetime import datetime
from typing import Literal, Sequence, NamedTuple, Self

from django.conf import settings
from elasticsearch import exceptions

from elasticsearch_control import (
    AbstractIndex,
    ElasticsearchPaginator,
    QueryLimitParams,
)
from elasticsearch_control.transport import elasticsearch_connector

T_Values = Literal["title", "content", "tags", "published_at"]


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

    class Meta:
        index_name = "company"
        connector = elasticsearch_connector
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
                    }
                },
            }
        }

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
        }

    @classmethod
    def get(cls, id_: str, values: Sequence[T_Values] = None, **kwargs) -> Self | None:
        """
        Возвращает заметку, если была найдена, в противном случае `None`.

        :param id_: Идентификатор заметки.
        :param values: Список полей, значения которых необходимы для возвращаемой заметки.
        :param kwargs: Дополнительные параметры для поиска.
        :return: Объект `PostIndex` или `None`.
        """

        # Если указано, какие именно поля требуется вернуть, тогда формируем дополнительные параметры запроса
        extra = {"_source": values} if values else {}
        # Вызываем родительский метод `get`
        response = super().get(id_=id_, **extra, **kwargs)

        if response is not None and response.get("_source"):  # Если получили ответ
            post = PostIndex()
            data: dict = response["_source"]

            # Если теги были получены и они в виде list, то переводим их в строку тегов, разделенную `, `
            if data.get("tags") and isinstance(data["tags"], list):
                data["tags"] = ", ".join(data["tags"])

            post.id = id_
            post.title = data.get("title", "")
            post.content = data.get("content", "")
            post.tags = data.get("tags", "")

            if data.get("published_at"):
                # Если дата была передана, то получаем объект из строки основываясь на следующем формате:
                # 2021-10-13T14:58:05.866799
                post.published_at = datetime.strptime(
                    data["published_at"][:19], "%Y-%m-%dT%H:%M:%S"
                )

            return post

        return None

    @classmethod
    def create(cls, title: str, tags: list[str], content: str) -> Self | None:
        """
        Создает новую заметку и возвращает её.

        :param title: Заголовок.
        :param tags: Список тегов.
        :param content: Содержимое.
        :return: Заметка, если была создана или None.
        """

        post = PostIndex()
        post.title = title
        post.tags = ", ".join(tags)
        post.content = content
        post.published_at = datetime.now()
        try:
            result = cls.Meta.connector.es.index(
                index=cls.Meta.index_name,
                document=post.json(),
                request_timeout=cls.Meta.connector.timeout,
            )
        except exceptions.ElasticsearchException:
            return None
        post.id = result.get("_id", "")
        return post

    def delete(self) -> bool:
        """
        При удалении заметки, удаляются также и все связанные с ней файлы
        """

        if (settings.MEDIA_ROOT / self.id).exists():
            # Если есть прикрепленные файлы
            shutil.rmtree(settings.MEDIA_ROOT / self.id)
        return super().delete()

    @classmethod
    def filter(
        cls,
        tags_in: list[str] = None,
        tags_off: list[str] = None,
        string: str = "",
        values: Sequence[T_Values] = None,
        sort: T_Values = None,
        sort_desc: bool = False,
    ) -> ElasticsearchPaginator:
        """
        Возвращает список записей, которые были отфильтрованы.

        :param tags_in: Теги, которые должны находиться у записи.
        :param tags_off: Теги, которые должны отсутствовать у записи.
        :param string: Поиск строки в title и content.
        :param values: Список полей, которые надо вернуть для каждой заметки, либо `None`, тогда вернутся все поля.
        :param sort: Поле, по которому необходимо отсортировать, по умолчанию нет сортировки.
        :param sort_desc: Изменить порядок сортировки на обратный порядок?
        :return: `ElasticsearchPaginator`.
        """

        # Если переменная tags_off не пустая, то она присваивается сама себе, иначе присваивается пустой список.
        tags_off = tags_off if tags_off else []
        # Если переменная tags_in не пустая, то она присваивается сама себе, иначе присваивается пустой список.
        tags_in = tags_in if tags_in else []

        # Теги всегда требуется возвращать
        if values is None:
            values = ["title", "content", "tags", "published_at"]
        if "tags" not in values:
            values.append("tags")

        # Определяем параметр сортировки, если был указан
        sort_parameter = {sort: "desc" if sort_desc else "asc"} if sort else None

        query_params = QueryLimitParams(
            index=cls.Meta.index_name,
            source=values,
            query={"bool": {"must": []}},
            sort=sort_parameter,
            request_timeout=cls.Meta.connector.timeout,
        )

        # Если переменная string пустая и переменная tags_in не пустая, то выполняется поиск по тегам.
        if tags_in:
            query_params.query["bool"]["must"].append(
                {
                    "match": {"tags": " ".join(tags_in)},
                }
            )

        # Поиск по строке в title и content
        if string:
            query_params.query["bool"]["must"].append(
                {
                    "simple_query_string": {
                        "query": string,
                        "fields": ["title^2", "content"],
                    }
                }
            )

        if tags_off:
            query_params.query["bool"]["must_not"] = [
                {
                    "match": {"tags": " ".join(tags_off)},
                }
            ]

        return ElasticsearchPaginator(
            es=cls.Meta.connector.es,
            params=query_params,
            convert_result=cls._convert_post_result,
            # extra
            tags_in=tags_in,
            tags_off=tags_off,
        )

    @staticmethod
    def _convert_post_result(
        res, tags_in: list[str], tags_off: list[str]
    ) -> list[dict]:
        # Присваивает переменной max_score максимальный балл из всех записей в ответе.
        max_score = float(res["hits"]["max_score"] or 1)
        result = []
        # Проверяет, есть ли хоть одна запись в ответе.
        if res and res["hits"]["total"]["value"]:
            for post in res["hits"]["hits"]:
                if isinstance(post["_source"]["tags"], str):
                    # Переводим один тег в список из одного тега
                    post["_source"]["tags"] = [post["_source"]["tags"]]
                # Если имеются необходимые теги (tags_in) и они встречаются в записи, а также
                # имеются нежелательные теги (tags_off) и они отсутствуют в записи
                # Пересечение тегов поста и тегов поиска равно списку тегов поиска (т.е. теги поиска содержатся в посте)
                if (
                    not tags_in
                    or sorted(list(set(post["_source"]["tags"]) & set(tags_in)))
                    == sorted(tags_in)
                ) and (
                    not tags_off or not set(post["_source"]["tags"]) & set(tags_off)
                ):
                    result.append(
                        {
                            "id": post["_id"],
                            "title": post["_source"].get("title"),
                            "tags": post["_source"].get("tags"),
                            "published_at": post["_source"].get("published_at"),
                            "content": post["_source"].get("content"),
                            "score": round(float(post["_score"] or 0) / max_score, 3),
                        }
                    )
        return result

    @classmethod
    def get_titles(cls, string: str, unavailable_tags: list[str]) -> list[str]:
        """
        ## Возвращает заголовки, которые соответствуют искомой строке.

        :param string: Строка для поиска.
        :param unavailable_tags: Недоступные пользователю теги.
        :return: Список заголовков, которые соответствуют искомой подстроке или пустой список.
        """

        # Поиск по строке в title и content
        res = cls.Meta.connector.es.search(
            index=cls.Meta.index_name,
            _source=["title", "tags"],
            query={
                "bool": {
                    "must": [
                        {
                            "simple_query_string": {
                                "query": string,
                                "fields": ["title^2"],
                            }
                        }
                    ],
                    "must_not": [
                        {"match": {"tags": " ".join(unavailable_tags)}},
                    ],
                }
            },
            request_timeout=cls.Meta.connector.timeout,
        )
        # Проверяет, есть ли хоть одна запись в ответе.
        if res["hits"]["total"]["value"]:
            return [line["_source"]["title"] for line in res["hits"]["hits"]]
        else:
            return []

    def get_files(self) -> list[PostFile]:
        """
        ## Возвращаем список файлов, которые прикреплены к заметке

        :return: Список файлов
        """

        files = []
        # Если существует папка для данного post_id и в ней есть файлы
        for f in (settings.MEDIA_ROOT / self.id).glob("*"):
            if f.is_file():
                # Добавляем имя файла + иконку в список
                files.append(
                    PostFile(
                        name=f.name,
                        size=f.stat().st_size,
                    )
                )
        return files

    @classmethod
    def tags_count(cls, tag_name: str):
        return cls.Meta.connector.es.count(
            index=cls.Meta.index_name,
            body={"query": {"match": {"tags": tag_name}}},
            request_timeout=settings.ELASTICSEARCH_TIMEOUT,
        )["count"]
