from django.core.cache import cache


class CacheVersion:
    def __init__(self, cache_name: str) -> None:
        self._cache_name = cache_name

    def get_version(self) -> int:
        return cache.get(f"{self._cache_name}:version", 1)

    def increment_version(self) -> None:
        try:
            cache.incr(f"{self._cache_name}:version", 1)
        except ValueError:
            cache.set(f"{self._cache_name}:version", 2)
