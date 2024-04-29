from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any


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

    def __new__(cls, cls_name, bases, attrs) -> type:
        annotations: dict = attrs.get("__annotations__", {})
        if annotations:
            # Если имеются аннотации типов в классе
            if not attrs.get("Meta"):
                raise NotImplementedError(f"Необходимо указать класс `Meta` для индекса `{cls_name}`")

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
                raise TypeError(f"Неверный формат поля `{field_name}` для индекса `{cls_name}`")

            # Определяем, какой тип будет по умолчанию для определенного поля по его аннотации
            attrs[field_name] = _types_base_value(annotation)

            # Добавляем mappings поля
            attrs["Meta"].mappings[field_name] = {"type": mtype}

            # Добавляем extra параметры, если указаны
            if hasattr(attrs["Meta"], "extra_field_props"):
                extra = attrs["Meta"].extra_field_props.get(field_name)
                if isinstance(extra, dict):
                    attrs["Meta"].mappings[field_name].update(extra)

        return super().__new__(cls, cls_name, bases, attrs)


class AbstractIndex(metaclass=MetaIndex):
    """
    Абстрактный класс, для управления индексом в Elasticsearch
    """

    id: str = ""

    @abstractmethod
    def json(self) -> dict:
        """
        Возвращает поля индекса в виде словаря
        """
        pass

    @classmethod
    def get_index_settings(cls) -> dict[str, Any]:
        """
        Возвращает все необходимые настройки индекса, для его создания в Elasticsearch.
        """

        return {
            "settings": cls.Meta.settings,
            "mappings": {
                "dynamic": "true",
                "properties": cls.Meta.mappings,
            },
        }

    class Meta(ABC):
        """
        Класс для управления индексом.
        """

        index_name: str
        settings: dict[str, Any]
        extra_field_props: dict[str, dict[str, Any]] = {}

        # Создается автоматически, не трогать
        mappings: dict[str, dict[str, Any]]
