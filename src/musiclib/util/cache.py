from collections.abc import Hashable
from typing import Any
from typing import ClassVar


class Cached:
    _cache: ClassVar[dict[tuple[type, tuple[Hashable, ...], frozenset[tuple[str, Hashable]]], Any]] = {}

    def __new__(cls, *args: Hashable, **kwargs: Hashable) -> Any:
        key = cls, args, frozenset(kwargs.items())
        instance = cls._cache.get(key)
        if instance is not None:
            return instance
        instance = super().__new__(cls)
        cls._cache[key] = instance
        return instance
