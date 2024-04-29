import uuid
from datetime import datetime

from django.conf import settings
from elasticsearch import Elasticsearch, exceptions

from elasticsearch_control import ElasticsearchPaginator
from elasticsearch_control.transport import es_connector
from .exc import NotFoundError, RepositoryException
from ..es_index import PostFile, PostIndex, T_Values
from ..filters import create_notes_query_params


class NotesRepository:

    def __init__(self, es: Elasticsearch, index: str, timeout: int = 5):
        self._es = es
        self._timeout = timeout
        self.index = index

    def get(self, id_: str, values: list[T_Values] | None = None) -> PostIndex:
        """
        Возвращает заметку, если была найдена

        :param id_: Идентификатор заметки.
        :param values: Список полей, значения которых необходимы для возвращаемой заметки.
        :raises NotFoundError: Если заметка не найдена.
        """
        try:
            response = self._es.get(
                index=self.index,
                id=id_,
                request_timeout=self._timeout,
                _source=list(values) if values else None,
            )
        except exceptions.ElasticsearchException:
            raise NotFoundError

        post = PostIndex()
        data: dict = response["_source"]

        # Если теги были получены и они в виде list, то переводим их в строку тегов, разделенную `, `
        if data.get("tags") and isinstance(data["tags"], list):
            data["tags"] = ", ".join(data["tags"])

        post.id = id_
        post.title = data.get("title", "")
        post.content = data.get("content", "")
        post.preview_image = data.get("preview_image", "")
        post.tags = data.get("tags", "")

        if data.get("published_at"):
            # Если дата была передана, то получаем объект из строки основываясь на следующем формате:
            # 2021-10-13T14:58:05.866799
            post.published_at = datetime.strptime(data["published_at"][:19], "%Y-%m-%dT%H:%M:%S")

        return post

    def create(self, title: str, tags: list[str], content: str, preview_image: str) -> PostIndex:
        """
        Создает новую заметку и возвращает её.

        :param title: Заголовок.
        :param tags: Список тегов.
        :param content: Содержимое.
        :param preview_image: Ссылка на изображение, которое будет отображено в браузере.
        :return: Заметка, если была создана или None.
        """

        post = PostIndex()
        post.title = title
        post.tags = ", ".join(tags)
        post.content = content
        post.published_at = datetime.now()
        post.preview_image = preview_image
        try:
            result = self._es.index(
                index=self.index, id=str(uuid.uuid4()), document=post.json(), request_timeout=self._timeout
            )
        except exceptions.ElasticsearchException:
            raise RepositoryException

        post.id = result.get("_id", "")
        return post

    def delete(self, id_: str) -> bool:
        """Удаляет запись"""
        try:
            result = self._es.delete(index=self.index, id=id_)
        except exceptions.ElasticsearchException:
            return False
        return result["_shards"].get("failed") == 0

    def update(self, id_: str, instance: dict, values: list[T_Values] | None = None):
        """
        Сохраняет переданные в списке `values` поля для текущей записи.
        Если `values` не были переданы, то сохраняет все поля.
        """

        if values is None:
            data = instance
        else:
            data = {k: v for k, v in instance.items() if k in values}
        try:
            self._es.update(index=self.index, id=id_, body={"doc": data}, request_timeout=self._timeout)
        except exceptions.ElasticsearchException:
            return False
        instance["id"] = id_
        return instance

    def filter(
        self,
        tags_in: list[str] | None = None,
        tags_off: list[str] | None = None,
        string: str = "",
        values: list[T_Values] | None = None,
        sort: T_Values | None = None,
        sort_desc: bool = False,
        convert_result=None,
    ):
        """
        Возвращает список записей, которые были отфильтрованы.

        :param tags_in: Теги, которые должны находиться у записи.
        :param tags_off: Теги, которые должны отсутствовать у записи.
        :param string: Поиск строки в title и content.
        :param values: Список полей, которые надо вернуть для каждой заметки, либо `None`, тогда вернутся все поля.
        :param sort: Поле, по которому необходимо отсортировать, по умолчанию нет сортировки.
        :param sort_desc: Изменить порядок сортировки на обратный порядок?
        :param convert_result: Функция, которая будет преобразовывать результат запроса в объект.
        :return: `ElasticsearchPaginator`.
        """
        query_params = create_notes_query_params(
            self.index,
            tags_in=tags_in or [],
            tags_off=tags_off or [],
            string=string,
            values=values,
            sort=sort,
            sort_desc=sort_desc,
            timeout=self._timeout,
        )
        return ElasticsearchPaginator(
            es=self._es,
            params=query_params,
            convert_result=convert_result,
            tags_in=tags_in,
            tags_off=tags_off,
        )

    def get_titles(self, string: str, unavailable_tags: list[str]) -> list[str]:
        """
        ## Возвращает заголовки, которые соответствуют искомой строке.

        :param string: Строка для поиска.
        :param unavailable_tags: Недоступные пользователю теги.
        :return: Список заголовков, которые соответствуют искомой подстроке или пустой список.
        """

        # Поиск по строке в title и content
        res = self._es.search(
            index=self.index,
            _source=["title", "tags"],
            query={
                "bool": {
                    "must": [
                        {
                            "match": {
                                "title": {"query": string, "fuzziness": "auto"},
                            },
                        },
                    ],
                    "must_not": [{"match": {"tags": " ".join(unavailable_tags)}}],
                }
            },
            request_timeout=self._timeout,
        )
        # Проверяет, есть ли хоть одна запись в ответе.
        if res["hits"]["total"]["value"]:
            return [line["_source"]["title"] for line in res["hits"]["hits"]]
        else:
            return []

    @staticmethod
    def get_files(id_: str) -> list[PostFile]:
        """
        ## Возвращаем список файлов, которые прикреплены к заметке

        :return: Список файлов
        """

        files = []
        # Если существует папка для данного post_id и в ней есть файлы
        for f in (settings.MEDIA_ROOT / id_).glob("*"):
            if f.is_file():
                # Добавляем имя файла + иконку в список
                files.append(PostFile(name=f.name, size=f.stat().st_size))
        return files

    def tags_count(self, tag_name: str) -> int:
        try:
            return self._es.count(
                index=self.index,
                body={"query": {"match": {"tags": tag_name}}},
                request_timeout=self._timeout,
            )["count"]
        except exceptions.ElasticsearchException:
            raise RepositoryException


_repo_instance: NotesRepository | None = None


def get_repository() -> NotesRepository:
    global _repo_instance
    if _repo_instance is None:
        _repo_instance = NotesRepository(es_connector.es, PostIndex.Meta.index_name, es_connector.timeout)
    return _repo_instance
