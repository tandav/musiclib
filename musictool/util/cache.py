from typing import Any


class Cached:
    _cache: dict[tuple[type, tuple[Any, ...], frozenset[tuple[str, Any]]], Any] = {}

    def __new__(cls, *args, **kwargs):
        key = cls, args, frozenset(kwargs.items())
        instance = cls._cache.get(key)
        if instance is not None:
            return instance
        instance = super().__new__(cls)
        cls._cache[key] = instance
        return instance
