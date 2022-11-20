import os
import time
import logging
import datetime

import requests
from pprint import pprint
from elasticsearch import Elasticsearch
from elasticsearch.client.indices import IndicesClient


# Установка значения переменной `ELASTICSEARCH_HOST` в значение переменной среды `ELASTICSEARCH_HOST`, если она
# существует, в противном случае она устанавливается в `localhost`.
ELASTICSEARCH_HOST = os.getenv("ELASTICSEARCH_HOST") or "localhost"

# Попытка получить значение переменной среды `ELASTICSEARCH_request_timeout` и преобразовать его в целое число. В случае
# неудачи устанавливается значение 20.
try:
    ELASTICSEARCH_request_timeout = (
        int(os.getenv("ELASTICSEARCH_request_timeout")) or 10
    )
except (ValueError, TypeError):
    ELASTICSEARCH_request_timeout = 20

# Он устанавливает уровень ведения журнала на ERROR и имя файла на logs.
logging.basicConfig(level=logging.ERROR, filename="logs")


def connect_elasticsearch() -> (Elasticsearch, None):
    """
    ## Подключается к серверу Elasticsearch и возвращает объект подключения.
    :return: Соединение с сервером Elasticsearch.
    """

    # Подключение к серверу Elasticsearch и возврат объекта подключения.
    _es = Elasticsearch([{"host": ELASTICSEARCH_HOST, "port": 9200}])
    if _es.ping():
        print("connect_elasticsearch: Connected")
    else:
        print("connect_elasticsearch: It could not connect!")
        return None
    return _es


def create_index(es_object, settings: dict, index_name="company") -> bool:
    """
    ## Создает индекс под названием **index_name** с настройками, указанными в словаре **settings**

    :param es_object: объект Elasticsearch
    :param settings: словарь с настройками для индекса
    :param index_name: Имя индекса, который вы хотите создать, defaults to company (optional)
    :return: Создан ```True``` или нет ```False```
    """
    created = False
    # index settings

    try:
        # Проверяет, НЕ существует ли индекс с именем index_name.
        if not IndicesClient(client=es_object).exists(index=index_name):
            # Создание индекса с именем `index_name` и настройками `settings`
            resp = requests.put(
                url=f"http://{ELASTICSEARCH_HOST}:9200/{index_name}?pretty",
                headers={"Content-Type": "application/json"},
                json=settings,
            )
            pprint(resp.json())
            print("Created Index")
        created = True
    # Перехват любого исключения и его печать.
    except Exception as ex:
        print(str(ex))
    finally:
        return created


def create_post(elastic_object: Elasticsearch, index_name: str, record: dict) -> dict:
    """
    ## Эта функция создает запись в Elasticsearch

    :param elastic_object: Объект Elasticsearch
    :param index_name: Имя индекса, в котором необходимо создать запись
    :param record: Запись, которая будет вставлена в индекс
    :return: Результат создания записи
    """
    result = {}
    try:
        result = elastic_object.index(
            index=index_name,
            document=record,
            request_timeout=ELASTICSEARCH_request_timeout,
        )
    except Exception as ex:
        print("Error in indexing data")
        print(str(ex))
    finally:
        return result


def update_post(elastic_object: Elasticsearch, index_name: str, record: dict, id_: str):
    """
    ## Обновляет существующую запись по id

    :param elastic_object: Объект Elasticsearch
    :param index_name: Имя индекса, в котором необходимо изменить запись
    :param record: Данные для обновления
    :param id_: ID записи
    :return: Результат изменения записи
    """

    result = {}
    try:
        result = elastic_object.index(
            index=index_name,
            document=record,
            id=id_,
            request_timeout=ELASTICSEARCH_request_timeout,
        )
    except Exception as ex:
        print("Error in indexing data")
        print(str(ex))
    finally:
        return result


def get_titles(elacticsearch: Elasticsearch, string: str, index="company"):
    """
    ## Возвращает названия записей, которые соответствуют строке.

    :param elacticsearch: Объект Elasticsearch
    :param string: Строка для поиска
    :param index: Имя индекса в elasticsearch, defaults to company (optional)
    :return: Список записей, которые соответствуют искомой подстроке или пустой список
    """

    # Поиск по строке в title и content
    res = elacticsearch.search(
        index=index,
        _source=["title"],
        query={"simple_query_string": {"query": string, "fields": ["title"]}},
        request_timeout=ELASTICSEARCH_request_timeout,
    )
    pprint(res)
    # Проверяет, есть ли хоть одна запись в ответе.
    if res["hits"]["total"]["value"]:
        return [line["_source"]["title"] for line in res["hits"]["hits"]]
    else:
        return []


def find_posts(
    elacticsearch: Elasticsearch,
    tags_in: list = None,
    tags_off: list = None,
    string: str = "",
) -> list:
    """
    ## Возвращает список записей, которые были отфильтрованы

    :param elacticsearch: Объект Elasticsearch
    :param tags_in: Теги, которые должны находиться у записи
    :param tags_off: Теги, которые должны отсутствовать у записи
    :param string: Поиск строки в title и content
    :return: ```[ {'id': 'id', 'title': 'Заголовок', 'tags': ['tag1', 'tag2']}, ... ]```
    """

    # Если переменная tags_off не пустая, то она присваивается сама себе, иначе присваивается пустой список.
    tags_off = tags_off if tags_off else []
    # Если переменная tags_in не пустая, то она присваивается сама себе, иначе присваивается пустой список.
    tags_in = tags_in if tags_in else []
    print("def find_posts(elacticsearch)", tags_in, tags_off, string)

    # Если переменная string пустая и переменная tags_in не пустая, то выполняется поиск по тегам.
    if not string and tags_in:
        # Поиск по тегам
        res = elacticsearch.search(
            size=1000,
            index="company",
            _source=["tags", "title"],
            query={"match": {"tags": " ".join(tags_in)}},
            request_timeout=ELASTICSEARCH_request_timeout,
        )
        pprint(res)

    elif string:
        # Поиск по строке в title и content
        res = elacticsearch.search(
            size=100,
            index="company",
            _source=["tags", "title"],
            query={
                "simple_query_string": {
                    "query": string,
                    "fields": ["title^2", "content"],
                }
            },
            request_timeout=ELASTICSEARCH_request_timeout,
        )
        pprint(res)
    else:
        return []

    # Присваивает переменной max_score максимальный балл из всех записей в ответе.
    max_score = float(res["hits"]["max_score"] or 0)
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
                not tags_in
                or sorted(list(set(post["_source"]["tags"]) & set(tags_in)))
                == sorted(tags_in)
            ) and (not tags_off or not set(post["_source"]["tags"]) & set(tags_off)):
                result.append(
                    {
                        "id": post["_id"],
                        "title": post["_source"]["title"],
                        "tags": post["_source"]["tags"],
                        "score": round(float(post["_score"]) / max_score, 3),
                    }
                )
    return result


def get_last_published(elacticsearch: Elasticsearch, index="company", limit=20):
    """
    ## Возвращает ```limit``` последних опубликованных записей из индекса ```index```

    :param elacticsearch: Объект Elasticsearch
    :param index: Имя индекса для поиска, defaults to company (optional)
    :param limit: Количество возвращаемых результатов, defaults to 6 (optional)
    """

    res = elacticsearch.search(
        index=index,
        body={"sort": {"published_at": "desc"}},
        size=limit,
        request_timeout=ELASTICSEARCH_request_timeout,
    )
    result = []
    if res and res["hits"]["total"]["value"]:
        for post in res["hits"]["hits"]:
            # COMPANY
            if index == "company":
                if isinstance(post["_source"]["tags"], str):
                    # Переводим один тег в список из одного тега
                    post["_source"]["tags"] = [post["_source"]["tags"]]
                result.append(
                    {
                        "id": post["_id"],
                        "title": post["_source"]["title"],
                        "tags": post["_source"]["tags"],
                        "score": 0,
                    }
                )
            # BOOKS
            elif index == "books":
                result.append(
                    {
                        "id": post["_id"],
                        "title": post["_source"]["title"],
                        "author": post["_source"]["author"],
                        "year": post["_source"]["year"],
                        "about": post["_source"]["about"],
                        "published_at": datetime.datetime.strptime(
                            post["_source"]["published_at"], "%Y-%m-%dT%H:%M:%S.%f"
                        ),
                    }
                )
    return result


def posts_count(index="company") -> int:
    """
    ## Возвращает количество записей в индексе

    :param index: Имя индекса для поиска, defaults to company (optional)
    """
    resp = requests.get(f"http://{ELASTICSEARCH_HOST}:9200/{index}/_doc/_count")
    if resp.status_code == 200:
        return resp.json()["count"]
    return -1


if __name__ == "__main__":
    settings_company = {
        "settings": {
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
        },
        "mappings": {
            "dynamic": "strict",
            "properties": {
                "title": {"type": "text"},
                "content": {"type": "text"},
                "tags": {"type": "text"},
                "published_at": {"type": "date"},
            },
        },
    }
    settings_books = {
        "settings": {
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
        },
        "mappings": {
            "dynamic": "strict",
            "properties": {
                "title": {"type": "text"},
                "author": {"type": "text"},
                "about": {"type": "text"},
                "year": {"type": "text"},
                "published_at": {"type": "date"},
            },
        },
    }
    # Создание индекса
    logging.basicConfig(filename="logs", level=logging.ERROR)
    print(os.getenv("ELASTICSEARCH_HOST"))
    while True:
        try:
            # Проверяем, работает ли elasticsearch или нет.
            # Если он запущен, он подключится к elasticsearch.
            es = connect_elasticsearch() or None
            if es:
                # Создаем индекс с именем company в Elasticsearch.
                create_index(es, settings_company, "company")
                # Создаем индекс с именем books в Elasticsearch.
                create_index(es, settings_books, "books")
                break
        except Exception as e:
            print(e)
            time.sleep(10)
