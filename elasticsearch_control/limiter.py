import math
from dataclasses import dataclass
from typing import Callable, Literal

from elasticsearch import Elasticsearch


@dataclass
class QueryLimitParams:
    """
    Необходимые параметры для создания запроса.
    """

    index: str
    source: list[str]
    query: dict
    request_timeout: int
    sort: dict[str, Literal["desc", "asc"]] | None = None

    @property
    def to_dict(self) -> dict:
        data = {
            "index": self.index,
            "_source": self.source,
            "query": self.query,
            "request_timeout": self.request_timeout,
        }
        if self.sort:
            data["sort"] = self.sort

        return data


class ElasticsearchPaginator:
    """
    Класс для пагинации запросов Elasticsearch.
    """

    per_page = 24

    def __init__(
        self,
        es: Elasticsearch,
        params: QueryLimitParams,
        convert_result: Callable = None,
        **extra
    ):
        """
        Инициализируем пагинатор запросов.

        :param es: Объект Elasticsearch для поиска
        :param params: Параметры содержащие в себе название индекса, какие поля требуется вернуть в запросе, тело
         запроса и таймаут ожидания
        :param convert_result: Функция, которой будет передан ответ от Elasticsearch. Данная функция может
         преобразовать неформатированные полученные данные.
        :param extra: Дополнительные параметры, которые будут переданы в функцию `convert_result` вместе с ответом
        """
        self._es = es
        self._params = params
        self.page = 1

        if params.query:
            # Определяем кол-во записей для текущего запроса
            self.count = self._es.count(
                index=params.index,
                body={"query": params.query},
                request_timeout=params.request_timeout,
            )["count"]
        else:
            self.count = 0

        self.max_pages = math.ceil(self.count / self.per_page)

        self._convert_func = convert_result
        self.extra_parameters = extra

    @property
    def has_previous(self):
        return self.page > 1

    @property
    def has_next(self):
        return (self.page + 1) <= self.max_pages

    def get_limits(self, page_num: int):
        from_ = (page_num - 1) * self.per_page
        return from_, self.per_page

    def get_page(self, page: str | int | float) -> list:
        """
        Получаем данные из конкретной страницы.

        :param page: Номер страницы.
        :return: Список найденных данных.
        """
        self.page = self.validate_number(page)
        if not self.count:
            return []
        query_from, query_size = self.get_limits(self.page)

        # Ищем данные по запросу
        res = self._es.search(
            **self._params.to_dict,
            **{"from_": query_from, "size": query_size},
        )

        # Вызываем функцию форматирования результата, его была указана
        if self._convert_func:
            return self._convert_func(res, **self.extra_parameters)

        if res.get("hits") and res["hits"].get("hits"):
            return res["hits"]["hits"]

        return []

    def validate_number(self, number: str | int | float) -> int:
        try:
            number = int(number)
        except (ValueError, TypeError):
            number = 1

        if self.max_pages and number > self.max_pages:
            number = self.max_pages
        elif number <= 0:
            number = 1
        return number
