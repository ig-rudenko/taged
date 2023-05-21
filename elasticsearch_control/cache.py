from typing import Callable, Any

from django.core.cache import cache


def get_or_cache(function: Callable, kwargs: dict, unique_name: str, cache_period: int) -> Any:
    """
    Возвращает результат из кэша django в случае нахождения в нем записи по ключу `unique_name`, если нет,
    то будет вызвана функция `function` и в неё будут переданы параметры `kwargs`.

    :param function: Функция для вызова.
    :param kwargs: Параметры функции.
    :param unique_name: Уникальное название для кэша.
    :param cache_period: Время хранения информации в кэше.
    """

    result = cache.get(unique_name)
    if not result:
        result = function(**kwargs)
        cache.set(unique_name, result, cache_period)
    return result
