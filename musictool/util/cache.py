class Cached:
    _cache = {}

    def __new__(cls, *args, **kwargs):
        key = args, frozenset(kwargs.items())
        if instance := cls._cache.get(key):
            return instance
        instance = super().__new__(cls)
        instance.__init__(*args, **kwargs)
        cls._cache[key] = instance
        return instance
