from functools import wraps
from typing import Callable

from django.http import JsonResponse
from elasticsearch.exceptions import TransportError
from rest_framework.request import Request


def api_elasticsearch_check_available(func: Callable):
    @wraps(func)
    def wrapper(request: Request, *args, **kwargs):
        try:
            return func(request, *args, **kwargs)
        except TransportError:
            return JsonResponse({"detail": "Elasticsearch недоступен"}, status=500)

    return wrapper
