import pathlib
import re
import shutil
from datetime import datetime
from typing import Optional, Sequence, Literal, List

import fitz
from django.conf import settings
from django.core.files import File
from elasticsearch import exceptions

from elasticsearch_control import (
    AbstractIndex,
    QueryLimitParams,
    ElasticsearchPaginator,
)
from elasticsearch_control.transport import elasticsearch_connector

T_Values = Literal["title", "author", "about", "year", "published_at"]


class BookIndex(AbstractIndex):
    """
    Индекс для книг.
    """

    title: str
    author: str
    about: str
    year: str
    published_at: datetime

    class Meta:
        index_name = "books"
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

    def json(self) -> dict:
        return {
            "title": self.title,
            "author": self.author,
            "about": self.about,
            "year": self.year,
            "published_at": self.published_at,
        }

    @classmethod
    def get(
        cls, id_: str, values: Optional[Sequence[T_Values]] = None, **kwargs
    ) -> Optional["BookIndex"]:
        """
        Возвращает книгу, если была найдена, в противном случае `None`.

        :param id_: Идентификатор книги.
        :param values: Список полей, значения которых необходимы для возвращаемой книги.
        :param kwargs: Дополнительные параметры для поиска.
        :return: Объект `BookIndex` или `None`.
        """

        # Если указано, какие именно поля требуется вернуть, тогда формируем дополнительные параметры запроса
        extra = {"_source": values} if values else {}
        # Вызываем родительский метод `get`
        response: dict = super().get(id_=id_, **extra, **kwargs)

        if response.get("_source"):  # Если получили ответ
            book = BookIndex()
            data: dict = response["_source"]

            book.id = id_
            book.title = data.get("title", "")
            book.author = data.get("author", "")
            book.about = data.get("about", "")
            book.year = data.get("year", "")

            if data.get("published_at"):
                # Если дата была передана, то получаем объект из строки основываясь на следующем формате:
                # 2021-10-13T14:58:05.866799
                book.published_at = datetime.strptime(
                    data["published_at"][:19], "%Y-%m-%dT%H:%M:%S"
                )

            return book

        return None

    @classmethod
    def create(
        cls, title: str, author: str, year: str, about: str
    ) -> Optional["BookIndex"]:
        """
        Создает новую заметку и возвращает её.

        :param title: Название книги.
        :param author: Автор(ы).
        :param year: Год.
        :param about: Описание книги.
        :return: Книга, если была создана или None.
        """

        book = BookIndex()
        book.title = title
        book.author = author
        book.year = year
        book.about = about
        book.published_at = datetime.now()
        try:
            result = cls.Meta.connector.es.index(
                index=cls.Meta.index_name,
                document=book.json(),
                request_timeout=cls.Meta.connector.timeout,
            )
        except exceptions.ElasticsearchException:
            return None
        book.id = result.get("_id", "")
        return book

    @classmethod
    def filter(
        cls,
        search: str = "",
        year: str = "",
        values: Optional[Sequence[T_Values]] = None,
        sort: T_Values = None,
        sort_desc: bool = False,
    ):
        """
        Возвращает список книг, которые были отфильтрованы.

        :param search: Строка поиска, совпадение которой будет искаться в названии книги, авторе и описании.
        :param year: Год, который необходимо искать.
        :param values: Список полей, которые надо вернуть для каждой заметки, либо `None`, тогда вернутся все поля.
        :param sort: Поле, по которому необходимо отсортировать, по умолчанию нет сортировки.
        :param sort_desc: Изменить порядок сортировки на обратный порядок?
        :return: `ElasticsearchPaginator`.
        """

        # Теги всегда требуется возвращать
        if values is None:
            values = ["title", "author", "year", "about", "published_at"]

        # Определяем параметр сортировки, если был указан
        sort_parameter = {sort: "desc" if sort_desc else "asc"} if sort else None

        query_params = QueryLimitParams(
            index=cls.Meta.index_name,
            source=values,
            query={"bool": {"must": []}},
            sort=sort_parameter,
            request_timeout=cls.Meta.connector.timeout,
        )

        if search:
            # Поиск текста
            query_params.query["bool"]["must"].append(
                {
                    "simple_query_string": {
                        "query": search,
                        "fields": ["title^2", "about", "author"],
                    }
                }
            )

        if year:
            # Поиск книг по годам
            query_params.query["bool"]["must"].append(
                {
                    "term": {"year": year},
                }
            )

        return ElasticsearchPaginator(
            es=cls.Meta.connector.es,
            params=query_params,
            convert_result=cls._convert_books_result,
        )

    @staticmethod
    def _convert_books_result(res: dict) -> List[dict]:
        result = []
        if res:
            # Создаем список книг с ключами id, title, year, author
            # Проходит по всем книгам из базы данных и добавляет их в список `res_books`.
            for b in res["hits"]["hits"]:
                # Создание нового словаря с ключами из `b["_source"]` и ключом `id` со значением `b["_id"]`.
                result.append(
                    {
                        "id": b["_id"],
                        "title": b["_source"].get("title", ""),
                        "author": b["_source"].get("author", ""),
                        "about": b["_source"].get("about", ""),
                        "year": b["_source"].get("year", ""),
                        "published_at": b["_source"].get("published_at", None),
                    }
                )
        return result

    def delete(self) -> bool:
        """
        Удаляем книгу и все файлы связанные с ней.
        :return:
        """
        # Удаляет папку с книгой.
        shutil.rmtree(settings.MEDIA_ROOT / "books" / self.id, ignore_errors=True)
        return super().delete()

    def get_file(self) -> Optional[pathlib.Path]:
        """
        Получаем файл книги.
        """

        book_folder = pathlib.Path(settings.MEDIA_ROOT / "books" / self.id)
        if not book_folder.exists():
            return None
        for file in book_folder.glob("*"):
            if file.name != "preview.png":
                return file
        return None

    def set_file(self, file_name: str, file: File):
        """
        Создаем для книги файл, а также превью для его просмотра.
        :param file_name: Имя файла.
        :param file: Сам файл, полученный от пользователя.
        """

        # Фильтруем запрещенные символы
        file_name = re.sub(r"[<>#%\"|^\[\]`;?:@&=+$ ]+", "_", file_name)
        # Создаем директорию для хранения книги
        book_folder = pathlib.Path(settings.MEDIA_ROOT / "books" / self.id)
        book_folder.mkdir(parents=True, exist_ok=True)

        # Удаляем старый файл книги
        old_file = self.get_file()
        if old_file:
            old_file.unlink(missing_ok=True)

        # Открытие файла в бинарном режиме.
        with (book_folder / file_name).open("wb+") as upload_file:
            # Чтение файла по частям, а затем его запись.
            for chunk_ in file.chunks():
                upload_file.write(chunk_)  # Записываем файл

        # Получаем расширение файла
        file_format = file_name.split(".")[-1]
        book_file_path = book_folder / file_name
        book_preview_path = book_folder / "preview.png"

        if file_format == "pdf":
            # Если книга в PDF формате, то превью будет первой страницей документа
            doc = fitz.Document(book_file_path.absolute())
            page = doc.load_page(0)
            pix = page.get_pixmap()
            pix.save(book_preview_path.absolute())
        elif file_format in ["png", "jpg", "jpeg", "svg"]:
            # Проверка, является ли файл изображением.
            # Превью будет этим же файлом
            shutil.copyfile(book_file_path, book_preview_path)
        else:
            # Нет превью книги (ставится заглушка `none_preview.png`)
            shutil.copyfile(
                f"{settings.BASE_DIR}/static/images/books/none_preview.png",
                book_preview_path,
            )
