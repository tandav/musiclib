from typing import Any

from musiclib import config
from musiclib.svg.isomorphic.hexagonal import Hexagonal
from musiclib.svg.isomorphic.squared import Squared


class ReprSVGMixin:
    def _repr_svg_(self, **kwargs: Any) -> str:
        method = getattr(self, config.repr_svg_config['method'])  # type: ignore[call-overload]
        kw = {**config.repr_svg_config['kwargs'], **kwargs}  # type: ignore[dict-item]
        plane_cls = kw.get('plane_cls')
        if plane_cls is not None:
            kw['plane_cls'] = {'Hexagonal': Hexagonal, 'Squared': Squared}[plane_cls]
        return str(method(**kw))
