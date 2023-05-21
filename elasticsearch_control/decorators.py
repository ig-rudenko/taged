from functools import wraps

from django.shortcuts import render
from elasticsearch.exceptions import TransportError


def elasticsearch_check_available(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        try:
            return func(request, *args, **kwargs)
        except TransportError:
            return render(request, "errors/elastic_unavailable.html", status=500)

    return wrapper
