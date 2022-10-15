from __future__ import annotations

from collections.abc import Sequence
from typing import overload

from musictool import config
from musictool.card import Card
from musictool.note import SpecificNote
from musictool.noteset import NoteSet

CHROMATIC_NOTESET = NoteSet(frozenset(config.chromatic_notes))


class NoteRange(Sequence[SpecificNote], Card):
    def __init__(
        self,
        start: SpecificNote | str,
        stop: SpecificNote | str,
        noteset: NoteSet = CHROMATIC_NOTESET,
    ):
        if isinstance(start, str):
            start = SpecificNote.from_str(start)
        if isinstance(stop, str):
            stop = SpecificNote.from_str(stop)

        """both ends included"""
        if start > stop:
            raise ValueError('start should be less than stop')

        if not {start.abstract, stop.abstract} <= noteset.notes:
            raise KeyError('start and stop notes should be in the noteset')

        self.start = start
        self.stop = stop
        self.noteset = noteset
        self._key = self.start, self.stop, self.noteset

    def _getitem_int(self, item: int) -> SpecificNote:
        if 0 <= item < len(self):
            q = self.noteset.add_note(self.start, item)
            return q
        elif -len(self) <= item < 0: return self.noteset.add_note(self.stop, item + 1)
        else: raise IndexError('index out of range')

    @overload
    def __getitem__(self, i: int) -> SpecificNote: ...

    @overload
    def __getitem__(self, s: slice) -> NoteRange: ...

    def __getitem__(self, item: int | slice) -> SpecificNote | NoteRange:
        if isinstance(item, int): return self._getitem_int(item)
        elif isinstance(item, slice):
            # if item.start is None:
            start = 0 if item.start is None else item.start
            stop = len(self) - 1 if item.stop is None else item.stop
            if not 0 <= start <= stop <= len(self):
                raise IndexError('NoteRange slice is out of range, negative indexing is not supported')
            return NoteRange(self._getitem_int(start), self._getitem_int(stop), self.noteset)
        else: raise TypeError(f'NoteRange indices must be integers or slices, got {type(item)}')

    def __contains__(self, item: object) -> bool:
        if not isinstance(item, SpecificNote):
            return False
        return item.abstract in self.noteset and self.start <= item <= self.stop

    def __iter__(self): return (self[i] for i in range(len(self)))
    def __repr__(self): return f'NoteRange({self.start}, {self.stop}, noteset={self.noteset})'
    def __len__(self): return self.noteset.subtract(self.stop, self.start) + 1
    def __eq__(self, other): return self._key == other._key
    def __hash__(self): return hash(self._key)

    def to_piano_image(self) -> str:
        from musictool.piano import Piano  # hack to fix circular import
        return Piano(
            note_colors=None if self.noteset is CHROMATIC_NOTESET else dict.fromkeys(self.noteset, config.RED),
            squares={self.start: {'text': str(self.start), 'text_size': '8'}, self.stop: {'text': str(self.stop), 'text_size': '8'}},
            noterange=NoteRange(self.start, self.stop),
        )._repr_svg_()

    def _repr_html_(
        self,
        html_classes: tuple[str, ...] = ('card',),
        title: str | None = None,
        subtitle: str | None = None,
        header_href: str | None = None,
        background_color: str | None = None,
    ) -> str:
        return self.repr_card(
            html_classes=html_classes,
            title=title or f'NoteRange({self.start}, {self.stop})',
            subtitle=subtitle,
            header_href=header_href,
            background_color=background_color,
            piano_html=self.to_piano_image(),
        )
