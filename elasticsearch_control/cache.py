from typing import Callable, Any

from django.core.cache import cache


def get_or_cache(
    function: Callable, kwargs: dict, unique_name: str, cache_timeout: int, version: int | None = None
) -> Any:
    """
    Возвращает результат из кэша django в случае нахождения в нем записи по ключу `unique_name`, если нет,
    то будет вызвана функция `function` и в неё будут переданы параметры `kwargs`.

    :param function: Функция для вызова.
    :param kwargs: Параметры функции.
    :param unique_name: Уникальное название для кэша.
    :param cache_timeout: Время хранения информации в кэше.
    :param version: Версия кэша.
    """

    result = cache.get(unique_name, default=None, version=version)
    if not result:
        result = function(**kwargs)
        cache.set(unique_name, result, cache_timeout, version=version)
    return result
