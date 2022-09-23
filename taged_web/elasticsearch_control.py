import datetime
import time

import requests
from elasticsearch import Elasticsearch
from elasticsearch.client.indices import IndicesClient
from pprint import pprint
import logging
import os


ELASTICSEARCH_HOST = os.environ.get('ELASTICSEARCH_HOST')
try:
    ELASTICSEARCH_request_timeout = int(os.environ.get('ELASTICSEARCH_request_timeout')) or 10
except (ValueError, TypeError):
    ELASTICSEARCH_request_timeout = 20

logging.basicConfig(level=logging.ERROR, filename='logs')


def connect_elasticsearch():
    _es = Elasticsearch([{'host': ELASTICSEARCH_HOST or 'localhost', 'port': 9200}])
    if _es.ping():
        print('connect_elasticsearch: Connected')
    else:
        print('connect_elasticsearch: It could not connect!')
        return None
    return _es


def create_index(es_object, settings: dict, index_name='company'):
    created = False
    # index settings

    try:
        if not IndicesClient(client=es_object).exists(index=index_name):
            resp = requests.put(
                url=f'http://{ELASTICSEARCH_HOST or "localhost"}:9200/{index_name}?pretty',
                headers={'Content-Type': 'application/json'},
                json=settings
            )
            pprint(resp.json())
            print('Created Index')
        created = True
    except Exception as ex:
        print(str(ex))
    finally:
        return created


def create_post(elastic_object: Elasticsearch, index_name: str, record: dict):
    """
    Создает запись
    :param elastic_object: Экземпляр класса Elasticsearch
    :param index_name: Имя индекса
    :param record: Данные для обновления
    :return:
    """
    try:
        return elastic_object.index(index=index_name, document=record, request_timeout=ELASTICSEARCH_request_timeout)
    except Exception as ex:
        print('Error in indexing data')
        print(str(ex))


def update_post(elastic_object: Elasticsearch, index_name: str, record: dict, id_: str):
    """
    Обновляет существующую запись по id
    :param elastic_object: Экземпляр класса Elasticsearch
    :param index_name: Имя индекса
    :param record: Данные для обновления
    :param id_: ID записи
    :return:
    """
    try:
        return elastic_object.index(index=index_name, document=record, id=id_,
                                    request_timeout=ELASTICSEARCH_request_timeout)

    except Exception as ex:
        print('Error in indexing data')
        print(str(ex))


def get_titles(elacticsearch: Elasticsearch, string: str, index='company'):
    # Поиск по строке в title и content
    res = elacticsearch.search(index=index, _source=['title'], query={
        "simple_query_string": {
            "query": string,
            "fields": [
                'title'
            ]
        }
    }, request_timeout=ELASTICSEARCH_request_timeout)
    pprint(res)
    if res['hits']['total']['value']:
        return [line['_source']['title'] for line in res['hits']['hits']]
    else:
        return []


def find_posts(elacticsearch: Elasticsearch, tags_in: list = None, tags_off: list = None, string: str = '') -> list:
    """
    Возвращает id записей, которые были отфильтрованы
    :param elacticsearch: Экземпляр класса Elasticsearch
    :param tags_in: Теги, которые должны находиться у записи
    :param tags_off: Теги, которые должны отсутствовать у записи
    :param string: Поиск строки в title и content
    :return: Список словарей [ {'id': id, 'title': title, 'tags': tags},  ]
    """
    tags_off = tags_off if tags_off else []
    tags_in = tags_in if tags_in else []
    print('def find_posts(elacticsearch)', tags_in, tags_off, string)
    if not string and tags_in:
        # Поиск по тегам
        res = elacticsearch.search(size=1000, index='company', _source=['tags', 'title'], query={
            "match": {
                "tags": " ".join(tags_in)
            }
        }, request_timeout=ELASTICSEARCH_request_timeout)
        pprint(res)

    elif string:
        # Поиск по строке в title и content
        res = elacticsearch.search(size=100, index='company', _source=['tags', 'title'], query={
            "simple_query_string": {
                "query": string,
                "fields": [
                    'title^2',
                    'content'
                ]
            }
        }, request_timeout=ELASTICSEARCH_request_timeout)
        pprint(res)
    else:
        return []

    max_score = float(res['hits']['max_score'] or 0)
    result = []
    if res and res['hits']['total']['value']:
        for post in res['hits']['hits']:
            if isinstance(post['_source']['tags'], str):
                post['_source']['tags'] = [post['_source']['tags']]  # Переводим один тег в список из одного тега
            # Если имеются необходимые теги (tags_in) и они встречаются в записи, а также
            # имеются нежелательные теги (tags_off) и они отсутствуют в записи
            # Пересечение тегов поста и тегов поиска равно списку тегов поиска (т.е. теги поиска содержатся в посте)
            if (not tags_in or sorted(list(set(post['_source']['tags']) & set(tags_in))) == sorted(tags_in)) \
                    and \
                    (not tags_off or not set(post['_source']['tags']) & set(tags_off)):
                result.append({
                    'id': post['_id'],
                    'title': post['_source']['title'],
                    'tags': post['_source']['tags'],
                    'score': round(float(post['_score'])/max_score, 3)
                })
    return result


def get_last_published(elacticsearch: Elasticsearch, index='company', limit=6):
    res = elacticsearch.search(index=index,
                               body={"sort": {"published_at": "desc"}},
                               size=limit,
                               request_timeout=ELASTICSEARCH_request_timeout)
    result = []
    if res and res['hits']['total']['value']:
        for post in res['hits']['hits']:
            # COMPANY
            if index == 'company':
                if isinstance(post['_source']['tags'], str):
                    post['_source']['tags'] = [post['_source']['tags']]  # Переводим один тег в список из одного тега
                result.append({
                    'id': post['_id'],
                    'title': post['_source']['title'],
                    'tags': post['_source']['tags'],
                    'score': 0
                })
            # BOOKS
            elif index == 'books':
                result.append({
                    'id': post['_id'],
                    'title': post['_source']['title'],
                    'author': post['_source']['author'],
                    'year': post['_source']['year'],
                    'about': post['_source']['about'],
                    'published_at': datetime.datetime.strptime(post['_source']['published_at'], '%Y-%m-%dT%H:%M:%S.%f')
                })
    return result


def posts_count(index='company') -> int:
    resp = requests.get(f'http://{ELASTICSEARCH_HOST or "localhost"}:9200/{index}/_doc/_count')
    if resp.status_code == 200:
        return resp.json()['count']
    return -1


if __name__ == '__main__':
    settings_company = {
        'settings': {
            "analysis": {
                "filter": {
                    "ru_stop": {
                        "type": "stop",
                        "stopwords": "_russian_"
                    },
                    "ru_stemmer": {
                        "type": "stemmer",
                        "language": "russian"
                    }
                },
                "analyzer": {
                    "default": {
                        "char_filter": [
                            "html_strip"
                        ],
                        "tokenizer": "standard",
                        "filter": [
                            "lowercase",
                            "ru_stop",
                            "ru_stemmer"
                        ]
                    }
                }
            }
        },
        "mappings": {
            "dynamic": "strict",
            "properties": {
                "title": {
                    "type": "text"
                },
                "content": {
                    "type": "text"
                },
                "tags": {
                    "type": "text"
                },
                "published_at": {
                    "type": "date"
                },
            }
        }
    }
    settings_books = {
        'settings': {
            "analysis": {
                "filter": {
                    "ru_stop": {
                        "type": "stop",
                        "stopwords": "_russian_"
                    },
                    "ru_stemmer": {
                        "type": "stemmer",
                        "language": "russian"
                    }
                },
                "analyzer": {
                    "default": {
                        "char_filter": [
                            "html_strip"
                        ],
                        "tokenizer": "standard",
                        "filter": [
                            "lowercase",
                            "ru_stop",
                            "ru_stemmer"
                        ]
                    }
                }
            }
        },
        "mappings": {
            "dynamic": "strict",
            "properties": {
                "title": {
                    "type": "text"
                },
                "author": {
                    "type": "text"
                },
                "about": {
                    "type": "text"
                },
                "year": {
                    "type": "text"
                },
                "published_at": {
                    "type": "date"
                },
            }
        }
    }
    # Создание индекса
    logging.basicConfig(filename='logs', level=logging.ERROR)
    print(os.environ.get('ELASTICSEARCH_HOST'))
    while True:
        try:
            es = connect_elasticsearch() or None
            if es:
                create_index(es, settings_company, 'company')
                create_index(es, settings_books, 'books')
                break
        except Exception as e:
            print(e)
            time.sleep(10)
