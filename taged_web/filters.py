from typing import Literal

from elasticsearch_control import QueryLimitParams
from .es_index import T_Values


def create_notes_query_params(
    index_name: str,
    *,
    tags_in: list[str],
    tags_off: list[str],
    string: str = "",
    values: list[T_Values] | None = None,
    sort: T_Values | None = None,
    sort_desc: bool = False,
    timeout: int = 5,
) -> QueryLimitParams:
    """
    Возвращает запрос для поиска заметок.

    :param index_name: Имя индекса.
    :param tags_in: Теги, которые должны находиться у записи.
    :param tags_off: Теги, которые должны отсутствовать у записи.
    :param string: Поиск строки в title и content.
    :param values: Список полей, которые надо вернуть для каждой заметки, либо `None`, тогда вернутся все поля.
    :param sort: Поле, по которому необходимо отсортировать, по умолчанию нет сортировки.
    :param sort_desc: Изменить порядок сортировки на обратный порядок?
    :param timeout: Время ожидания в секундах.
    :return: :class:`QueryLimitParams`.
    """

    # Если переменная tags_off не пустая, то она присваивается сама себе, иначе присваивается пустой список.
    tags_off = tags_off if tags_off else []
    # Если переменная tags_in не пустая, то она присваивается сама себе, иначе присваивается пустой список.
    tags_in = tags_in if tags_in else []

    # Теги всегда требуется возвращать
    source_values: list[str]
    if values is None:
        source_values = ["title", "content", "tags", "published_at", "preview_image"]
    else:
        source_values = list(values)
    if "tags" not in source_values:
        source_values.append("tags")

    # Определяем параметр сортировки, если был указан
    sort_parameter: dict[str, Literal["desc", "asc"]] | None = (
        {sort: "desc" if sort_desc else "asc"} if sort else None
    )

    query_params = QueryLimitParams(
        index=index_name,
        source=source_values,
        query={"bool": {"must": []}},
        sort=sort_parameter,
        request_timeout=timeout,
    )

    # Если переменная string пустая и переменная tags_in не пустая, то выполняется поиск по тегам.
    if tags_in:
        query_params.query["bool"]["must"].append(
            {
                "match": {"tags": " ".join(tags_in)},
            }
        )

    # Поиск по строке в title и content с возможностью допущения ошибок в словах.
    if string:
        query_params.query["bool"]["should"] = [
            {
                "match": {
                    "title": {"query": string, "fuzziness": "auto"},
                },
            },
            {
                "match": {
                    "content": {"query": string, "fuzziness": "auto"},
                },
            },
        ]
        query_params.query["bool"]["minimum_should_match"] = 1

    if tags_off:
        query_params.query["bool"]["must_not"] = [
            {
                "match": {"tags": " ".join(tags_off)},
            }
        ]

    return query_params


def notes_records_filter(res, tags_in: list[str], tags_off: list[str]) -> list[dict]:
    """
    Фильтрует полученные данные по тегам и приводит к формату записи.

    :param res: Результат запроса.
    :param tags_in: Теги, которые должны находиться у записи.
    :param tags_off: Теги, которые должны отсутствовать у записи.
    :return: Список отфильтрованных записей.
    """
    # Присваивает переменной max_score максимальный балл из всех записей в ответе.
    max_score = float(res["hits"]["max_score"] or 1)
    result = []
    # Проверяет, есть ли хоть одна запись в ответе.
    if res and res["hits"]["total"]["value"]:
        for post in res["hits"]["hits"]:
            if isinstance(post["_source"]["tags"], str):
                # Переводим один тег в список из одного тега
                post["_source"]["tags"] = [post["_source"]["tags"]]
            # Если имеются необходимые теги (tags_in) и они встречаются в записи, а также
            # имеются нежелательные теги (tags_off) и они отсутствуют в записи
            # Пересечение тегов поста и тегов поиска равно списку тегов поиска (т.е. теги поиска содержатся в посте)
            if (
                not tags_in or sorted(list(set(post["_source"]["tags"]) & set(tags_in))) == sorted(tags_in)
            ) and (not tags_off or not set(post["_source"]["tags"]) & set(tags_off)):
                result.append(
                    {
                        "id": post["_id"],
                        "title": post["_source"].get("title"),
                        "tags": post["_source"].get("tags"),
                        "published_at": post["_source"].get("published_at"),
                        "content": post["_source"].get("content"),
                        "preview_image": post["_source"].get("preview_image"),
                        "score": round(float(post["_score"] or 0) / max_score, 3),
                    }
                )
    return result
