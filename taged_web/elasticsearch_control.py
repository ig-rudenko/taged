import requests
from elasticsearch import Elasticsearch
from elasticsearch.client.indices import IndicesClient
from pprint import pprint
import logging
import os


ELASTICSEARCH_HOST = os.environ.get('ELASTICSEARCH_HOST')
logging.basicConfig(level=logging.ERROR, filename='logs')


def connect_elasticsearch():
    _es = None
    try:
        _es = Elasticsearch([{'host': ELASTICSEARCH_HOST or 'localhost', 'port': 9200}])
    except requests.ConnectionError:
        pass
    if _es.ping():
        print('Yay Connect')
    else:
        print('Awww it could not connect!')
    return _es


def create_index(es_object, index_name='company'):
    created = False
    # index settings
    settings = {
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
    try:
        if not IndicesClient(client=es_object).exists(index=index_name):
            resp = requests.put(
                url=f'http://{ELASTICSEARCH_HOST}:9200/{index_name}?pretty',
                headers={'Content-Type': 'application/json'},
                json=settings
            )
            print(resp.json())
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
        return elastic_object.index(index=index_name, document=record)
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
        return elastic_object.index(index=index_name, document=record, id=id_)

    except Exception as ex:
        print('Error in indexing data')
        print(str(ex))


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
    res = None
    if not string:
        # Поиск по тегам
        res = elacticsearch.search(index='company', _source=['tags', 'title'], query={
            "match": {
                "tags": " ".join(tags_in)
            }
        })
        pprint(res)
    else:

        # Поиск по строке в title и content
        res = elacticsearch.search(index='company', _source=['tags', 'title'], query={
            "simple_query_string": {
                "query": string,
                "fields": [
                    'title^2',
                    'content'
                ]
            }
        })
        pprint(res)

    result = []
    if res and res['hits']['total']['value']:
        for post in res['hits']['hits']:
            if isinstance(post['_source']['tags'], str):
                post['_source']['tags'] = [post['_source']['tags']]  # Переводим один тег в список из одного тега
            # Если имеются необходимые теги (tags_in) и они встречаются в записе, а также
            # имеются нежелательные теги (tags_off) и они отсутствуют в записе
            # Пересечение тегов поста и тегов поиска равно списку тегов поиска (т.е. теги поиска содержатся в посте)
            if (not tags_in or sorted(list(set(post['_source']['tags']) & set(tags_in))) == sorted(tags_in)) \
                    and \
                    (not tags_off or not set(post['_source']['tags']) & set(tags_off)):
                result.append({
                    'id': post['_id'],
                    'title': post['_source']['title'],
                    'tags': post['_source']['tags']
                })
    pprint(result)
    return result


if __name__ == '__main__':
    # Создание индекса
    logging.basicConfig(filename='logs', level=logging.ERROR)
    print(os.environ.get('ELASTICSEARCH_HOST'))
    while True:
        try:
            es = connect_elasticsearch() or None
            if es:
                create_index(es, 'company')
                break
        except Exception as e:
            print(e)

