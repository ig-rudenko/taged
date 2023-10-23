from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Self

from elasticsearch import exceptions

from .limiter import ElasticsearchPaginator
from .transport import ElasticsearchConnection


def _map_type(annotation: Any) -> str | None:
    if annotation == str:
        mtype = "text"
    elif annotation == int:
        mtype = "integer"
    elif annotation == float:
        mtype = "float"
    elif annotation == bool:
        mtype = "boolean"
    elif annotation == datetime:
        mtype = "date"
    elif annotation == bytes:
        mtype = "binary"
    elif annotation == dict:
        mtype = "object"
    else:
        return None
    return mtype


def _types_base_value(type_: Any) -> str | bytes | int | float | bool | dict | None:
    """
    Определяем, какой тип будет по умолчанию для определенного поля по его аннотации.

    :param type_: Тип
    :return: Значения этого типа по умолчанию
    """
    if type_ in [str, bytes, int, float, bool, dict]:
        return type_()
    return None


class MetaIndex(type):
    """
    Метакласс для декларативного создания класса для индекса Elasticsearch
    """

    def __new__(cls, cls_name, bases, attrs):
        annotations: dict = attrs.get("__annotations__", {})
        if annotations:
            # Если имеются аннотации типов в классе
            if not attrs.get("Meta"):
                raise NotImplementedError(
                    f"Необходимо указать класс `Meta` для индекса `{cls_name}`"
                )

            attrs["Meta"].mappings = {}
            del attrs["__annotations__"]

        # Идентификатор объекта индекса, используется для поиска записи в Elasticsearch
        attrs["id"] = None

        for field_name, annotation in annotations.items():
            if field_name == "id":
                continue  # Пропускаем поле идентификатора, его значение будет None по умолчанию

            # Определяем тип поля для elasticsearch по его аннотации python
            mtype = _map_type(annotation)
            if mtype is None:
                raise TypeError(
                    f"Неверный формат поля `{field_name}` для индекса `{cls_name}`"
                )

            # Определяем, какой тип будет по умолчанию для определенного поля по его аннотации
            attrs[field_name] = _types_base_value(annotation)

            # Добавляем mappings поля
            attrs["Meta"].mappings[field_name] = {"type": mtype}

        return super().__new__(cls, cls_name, bases, attrs)


class AbstractIndex(metaclass=MetaIndex):
    """
    Абстрактный класс, для управления индексом в Elasticsearch
    """

    id: str | None = None

    @classmethod
    @abstractmethod
    def create(cls, *args, **kwargs) -> Self | None:
        """
        Создание нового индекса
        """
        pass

    @classmethod
    @abstractmethod
    def filter(cls, *args, **kwargs) -> ElasticsearchPaginator:
        """
        Возврат списка записей в индексе по указанным параметрам
        """
        pass

    @abstractmethod
    def json(self) -> dict:
        """
        Возвращает поля индекса в виде словаря
        """
        pass

    @classmethod
    def get(cls, id_, *args, **kwargs) -> dict | Any:
        """
        Возвращает одну запись из индекса по его `id`, либо `None` если такой записи нет.
        """

        try:
            response = cls.Meta.connector.es.get(
                index=cls.Meta.index_name,
                id=id_,
                request_timeout=cls.Meta.connector.timeout,
                **kwargs,
            )
            return response
        except exceptions.ElasticsearchException:
            return None

    def delete(self) -> bool:
        """
        Удаляет текущую запись
        """

        try:
            result = self.Meta.connector.es.delete(
                index=self.Meta.index_name, id=self.id
            )
        except exceptions.ElasticsearchException:
            return False
        return result["_shards"].get("failed") == 0

    def save(self, values: list[str] = None) -> bool:
        """
        Сохраняет переданные в списке `values` поля для текущей записи.
        Если `values` не были переданы, то сохраняет все поля.

        :param values: Список полей индекса. (default None)
        """

        if not values:
            data = self.json()
        else:
            data = {k: v for k, v in self.json().items() if k in values}

        try:
            result = self.Meta.connector.es.update(
                index=self.Meta.index_name,
                id=self.id,
                body={"doc": data},
                request_timeout=self.Meta.connector.timeout,
            )
            self.id = result["_id"]
        except exceptions.ElasticsearchException:
            return False
        return result["_shards"].get("failed") == 0

    @classmethod
    def get_index_settings(cls) -> dict[str, Any]:
        """
        Возвращает все необходимые настройки индекса, для его создания в Elasticsearch.
        """

        return {
            "settings": cls.Meta.settings,
            "mappings": {
                "dynamic": "strict",
                "properties": cls.Meta.mappings,
            },
        }

    class Meta(ABC):
        """
        Класс для управления индексом.
        """

        connector: ElasticsearchConnection
        index_name: str
        settings: dict[str, Any]

        # Создается автоматически, не трогать
        mappings: dict[str, dict[str, Any]]
