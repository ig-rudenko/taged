from typing import Optional

from elasticsearch import Elasticsearch


class ElasticsearchConnection:
    """
    Связь с Elasticsearch.
    """

    def __init__(self):
        self.es: Optional[Elasticsearch] = None
        self.timeout = None

    def init(self, es: Elasticsearch, timeout: int) -> None:
        """
        Инициализируем подключение к Elasticsearch.
        :param es: Объект Elasticsearch.
        :param timeout: Таймаут запросов.
        """

        self.es = es
        self.timeout = timeout


elasticsearch_connector = ElasticsearchConnection()
