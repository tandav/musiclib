from typing import Any
from musiclib import config


class ReprSVGMixin:
    def _repr_svg_(self, **kwargs: Any) -> str:
        return str(getattr(self, config.repr_svg_method)(**kwargs))

