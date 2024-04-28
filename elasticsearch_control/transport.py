from elasticsearch import Elasticsearch, TransportError


class ElasticsearchConnection:
    """
    Связь с Elasticsearch.
    """

    def __init__(self):
        self._es: Elasticsearch | None = None
        self.timeout: int = 5

    @property
    def es(self) -> Elasticsearch:
        if self._es is None:
            raise TransportError("Elasticsearch is not connected")
        return self._es

    def init(self, es: Elasticsearch, timeout: int) -> None:
        """
        Инициализируем подключение к Elasticsearch.
        :param es: Объект Elasticsearch.
        :param timeout: Таймаут запросов.
        """

        self._es = es
        self.timeout = timeout


es_connector: ElasticsearchConnection = ElasticsearchConnection()
