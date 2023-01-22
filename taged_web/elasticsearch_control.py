import requests
from django.conf import settings
from pprint import pprint
from elasticsearch import Elasticsearch
from elasticsearch.client.indices import IndicesClient


class QueryLimit:
    per_page = 50

    def __init__(
        self, es: "ElasticsearchConnect", query: dict, convert_result=None, **extra
    ):
        self._es = es
        self._query = query
        if query["query"]:
            self.count = es.query_count(query["index"], query["query"])
        else:
            self.count = 0
        self._convert_func = convert_result
        self.extra_parameters = extra

    def get_limits(self, page_num: int):
        number = self.validate_number(page_num)
        bottom = (number - 1) * self.per_page
        top = bottom + self.per_page
        return bottom, top

    def get_page(self, page: int) -> list:
        if not self.count:
            return []
        query_from, query_size = self.get_limits(page)
        res = self._es.search(
            **self._query,
            **{"from_": query_from, "size": query_size},
        )

        if self._convert_func:
            return self._convert_func(res, **self.extra_parameters)

    def validate_number(self, number: int):
        try:
            number = int(number)
        except (ValueError, TypeError):
            number = 1

        if number > self.count:
            number = self.count
        elif number <= 0:
            number = 1
        return number


class ElasticsearchConnect(Elasticsearch):
    def __init__(self):
        super().__init__([{"host": settings.ELASTICSEARCH_HOST, "port": 9200}])

    def available(self) -> bool:
        if self.ping():
            return True
        else:
            print("No ping")
            return False

    def create_index(self, settings_: dict, index_name) -> bool:
        """
        ## Создает индекс под названием **index_name** с настройками, указанными в словаре **settings**

        :param settings_: словарь с настройками для индекса
        :param index_name: Имя индекса, который вы хотите создать
        :return: Создан ```True``` или нет ```False```
        """
        created = False
        # index settings
        print("create index", index_name)
        try:
            # Проверяет, НЕ существует ли индекс с именем index_name.
            if not IndicesClient(client=self).exists(index=index_name):
                # Создание индекса с именем `index_name` и настройками `settings`
                resp = requests.put(
                    url=f"http://{settings.ELASTICSEARCH_HOST}:9200/{index_name}?pretty",
                    headers={"Content-Type": "application/json"},
                    json=settings_,
                )
                pprint(resp.json())
                print("Created Index")
            created = True
        # Перехват любого исключения и его печать.
        except Exception as ex:
            print(str(ex))
        finally:
            return created

    def create_post(self, index_name: str, record: dict) -> dict:
        """
        ## Создает запись в Elasticsearch

        :param index_name: Имя индекса, в котором необходимо изменить запись.
        :param record: Запись, которая будет вставлена в индекс.
        :return: Результат создания записи.
        """
        result = {}
        try:
            result = self.index(
                index=index_name,
                document=record,
                request_timeout=settings.ELASTICSEARCH_TIMEOUT,
            )
        except Exception as ex:
            print("Error in indexing data")
            print(str(ex))
        finally:
            return result

    def update_post(self, index_name: str, record: dict, id_: str):
        """
        ## Обновляет существующую запись по id

        :param index_name: Имя индекса, в котором необходимо изменить запись
        :param record: Данные для обновления
        :param id_: ID записи
        :return: Результат изменения записи
        """

        result = {}
        try:
            result = self.index(
                index=index_name,
                document=record,
                id=id_,
                request_timeout=settings.ELASTICSEARCH_TIMEOUT,
            )
        except Exception as ex:
            print("Error in indexing data")
            print(str(ex))
        finally:
            return result

    def get_titles(self, string: str, index="company"):
        """
        ## Возвращает названия записей, которые соответствуют строке.

        :param string: Строка для поиска
        :param index: Имя индекса в elasticsearch, defaults to company (optional)
        :return: Список записей, которые соответствуют искомой подстроке или пустой список
        """

        # Поиск по строке в title и content
        res = self.search(
            index=index,
            _source=["title"],
            query={"simple_query_string": {"query": string, "fields": ["title"]}},
            request_timeout=settings.ELASTICSEARCH_TIMEOUT,
        )
        # Проверяет, есть ли хоть одна запись в ответе.
        if res["hits"]["total"]["value"]:
            return [line["_source"]["title"] for line in res["hits"]["hits"]]
        else:
            return []

    def query_count(self, index: str, query: dict) -> int:
        return self.count(
            index=index,
            body={"query": query},
            request_timeout=settings.ELASTICSEARCH_TIMEOUT,
        )["count"]

    def find_posts(
        self,
        tags_in: list = None,
        tags_off: list = None,
        string: str = "",
    ) -> QueryLimit:
        """
        ## Возвращает список записей, которые были отфильтрованы

        :param tags_in: Теги, которые должны находиться у записи
        :param tags_off: Теги, которые должны отсутствовать у записи
        :param string: Поиск строки в title и content
        :return: ```[ {'id': 'id', 'title': 'Заголовок', 'tags': ['tag1', 'tag2']}, ... ]```
        """

        # Если переменная tags_off не пустая, то она присваивается сама себе, иначе присваивается пустой список.
        tags_off = tags_off if tags_off else []
        # Если переменная tags_in не пустая, то она присваивается сама себе, иначе присваивается пустой список.
        tags_in = tags_in if tags_in else []

        # Если переменная string пустая и переменная tags_in не пустая, то выполняется поиск по тегам.
        if not string and tags_in:
            query = {"match": {"tags": " ".join(tags_in)}}

        # Поиск по строке в title и content
        elif string:
            query = {
                "simple_query_string": {
                    "query": string,
                    "fields": ["title^2", "content"],
                }
            }
        else:
            query = {}

        # Вычисляем кол-во записей по запросу
        query = {
            "index": "company",
            "_source": ["tags", "title"],
            "query": query,
            "request_timeout": settings.ELASTICSEARCH_TIMEOUT,
        }

        # Вычисляем отступ и размер выборки
        return QueryLimit(
            es=self,
            query=query,
            convert_result=self.convert_post_result,
            tags_in=tags_in,
            tags_off=tags_off,
        )

    @staticmethod
    def convert_post_result(res, tags_in, tags_off):
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
                ) and (
                    not tags_off or not set(post["_source"]["tags"]) & set(tags_off)
                ):
                    result.append(
                        {
                            "id": post["_id"],
                            "title": post["_source"]["title"],
                            "tags": post["_source"]["tags"],
                            "score": round(float(post["_score"]) / max_score, 3),
                        }
                    )
        return result

    def find_books(self, search: str = "", year: str = "") -> QueryLimit:
        query = {"bool": {"must": []}}

        if search:
            # Поиск текста
            query["bool"]["must"].append(
                {
                    "simple_query_string": {
                        "query": search,
                        "fields": ["title^2", "about", "author"],
                    }
                }
            )

        if year:
            # Поиск книг по годам
            query["bool"]["must"].append({"term": {"year": year},})

        return QueryLimit(
            es=self,
            query={
                "index": "books",
                "_source": ["title", "year", "author"],
                "query": query,
                "request_timeout": settings.ELASTICSEARCH_TIMEOUT,
            },
            convert_result=self.convert_books_result,
        )

    @staticmethod
    def convert_books_result(res: dict) -> list:
        result = []
        if res:
            # Создаем список книг с ключами id, title, year, author
            # Проходит по всем книгам из базы данных и добавляет их в список `res_books`.
            for b in res["hits"]["hits"]:
                # Создание нового словаря с ключами из `b["_source"]` и ключом `id` со значением `b["_id"]`.
                result.append(dict(b["_source"], **{"id": b["_id"]}))
        return result

    def get_last_published(self, index, limit=QueryLimit.per_page):
        """
        ## Возвращает ```limit``` последних опубликованных записей из индекса ```index```

        :param index: Имя индекса для поиска, defaults to company (optional)
        :param limit: Количество возвращаемых результатов, defaults to 20 (optional)
        """

        res = self.search(
            index=index,
            body={"sort": {"published_at": "desc"}},
            size=limit,
            request_timeout=settings.ELASTICSEARCH_TIMEOUT,
        )
        result = []
        if res and res["hits"]["total"]["value"]:
            for b in res["hits"]["hits"]:
                result.append(dict(b["_source"], **{"id": b["_id"], "score": 0}))
        return result

    @staticmethod
    def posts_count(index="company") -> int:
        """
        ## Возвращает количество записей в индексе

        :param index: Имя индекса для поиска, defaults to company (optional)
        """
        resp = requests.get(
            f"http://{settings.ELASTICSEARCH_HOST}:9200/{index}/_doc/_count"
        )
        if resp.status_code == 200:
            return resp.json()["count"]
        return -1
