from typing import Type

from elasticsearch import Elasticsearch
from requests.exceptions import ConnectionError

from .base_index import AbstractIndex
from .transport import ElasticsearchConnection, elasticsearch_connector


class IndexRegister:
    """
    Регистрирует индексы в Elasticsearch.
    """

    def __init__(self, es_connector: ElasticsearchConnection = elasticsearch_connector):
        self._es: Elasticsearch = es_connector.es

    def register_index(self, index: Type[AbstractIndex]) -> None:
        """
        Регистрирует индекс в Elasticsearch.
        :param index: Класс индекса.
        """
        self._validate_index(index)

        if self._es.ping():
            # Создаем индекс в Elasticsearch
            self._es.indices.create(
                index=index.Meta.index_name, body=index.get_index_settings(), ignore=400
            )
        else:
            raise ConnectionError("Elasticsearch недоступен!")

    def _validate_index(self, index) -> None:
        """
        Проверяет класс индекса на наличие в нем требуемых параметров и вызывает ошибки в случае отсутствия.
        :param index: Класс индекса.
        """
        if not issubclass(index, AbstractIndex):
            raise TypeError(
                f"Индекс `{index.__class__}` должен быть унаследован от `AbstractIndex`"
            )

        if not hasattr(index, "Meta"):
            raise NotImplementedError(
                f"Индекс `{index.__class__}` должен содержать класс Meta с настройками"
            )

        if not hasattr(index.Meta, "index_name"):
            raise ValueError(
                f"Не указано название `index_name` индекса `{index.__class__}` во внутреннем классе `Meta`"
            )

        if not hasattr(index.Meta, "settings"):
            raise ValueError(
                f"Не указаны настройки `settings` индекса `{index.__class__}` во внутреннем классе `Meta`"
            )

        if not hasattr(index.Meta, "mappings"):
            raise ValueError(
                f"Не указаны настройки `mappings` индекса `{index.__class__}` во внутреннем классе `Meta`"
            )
