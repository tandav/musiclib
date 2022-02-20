class Cached:
    _cache = {}

    def __new__(cls, *args, **kwargs):
        key = args, frozenset(kwargs.items())
        instance = cls._cache.get(key)
        if instance is not None:
            return instance
        instance = super().__new__(cls)
        instance.__init__(*args, **kwargs)
        cls._cache[key] = instance
        return instance
