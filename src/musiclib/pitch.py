import math

from musiclib.note import SpecificNote

A4 = SpecificNote('A', 4)


class Pitch:
    def __init__(
        self,
        hz_tuning: float = 440,
        origin_note: SpecificNote = A4,
    ) -> None:
        """
        origin_note: in midi format, A4 midi ~ 440Hz ~ midi number i=69
        """
        self.hz_tuning = hz_tuning
        self.origin_note = origin_note

    def i_to_hz(self, i: float) -> float:
        return self.hz_tuning * 2 ** ((i - self.origin_note.i) / 12)

    def hz_to_i(self, hz: float) -> float:
        return 12 * math.log2(hz / self.hz_tuning) + self.origin_note.i

    def note_to_hz(self, note: SpecificNote) -> float:
        return self.i_to_hz(note.i)

    def hz_to_note(self, hz: float) -> SpecificNote:
        return SpecificNote.from_i(round(self.hz_to_i(hz)))

    @staticmethod
    def hz_to_px(hz: float, hz_min: float, hz_max: float, px_max: float) -> float:
        """Convert Hz to pixel position (using logarithmic scale)"""
        return math.log2(hz / hz_min) / math.log2(hz_max / hz_min) * px_max

    @staticmethod
    def px_to_hz(px: float, hz_min: float, hz_max: float, px_max: float) -> float:
        """Convert pixel position to hz (assuming pixel using logarithmic scale)"""
        c = px / px_max
        return hz_min ** (1 - c) * hz_max ** c  # type: ignore[no-any-return]

    def __repr__(self) -> str:
        return f'Pitch(hz_tuning={self.hz_tuning!r}, origin_note={self.origin_note!r})'
