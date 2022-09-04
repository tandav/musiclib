import math

from musictool.note import SpecificNote


class Pitch:
    def __init__(
        self,
        hz_tuning: float = 440,
        origin_note: SpecificNote = SpecificNote('A', 5),
        transpose: float = 0,
    ):
        self.hz_tuning = hz_tuning
        self.origin_note = origin_note
        self.transpose = transpose

    def i_to_hz(self, i: float) -> float:
        return self.hz_tuning * 2 ** ((i + self.transpose) / 12)

    def hz_to_i(self, hz: float) -> float:
        return 12 * math.log2(hz / self.hz_tuning) - self.transpose

    def note_i_to_hz(self, note_i: float) -> float:
        return self.i_to_hz(note_i - self.origin_note.i)

    def hz_to_note_i(self, hz: float) -> float:
        return self.origin_note.i + self.hz_to_i(hz)

    def note_to_hz(self, note: SpecificNote) -> float:
        return self.note_i_to_hz(note.i)

    def hz_to_note(self, hz: float) -> SpecificNote:
        return SpecificNote.from_i(int(self.hz_to_note_i(hz)))

    @staticmethod
    def hz_to_px(hz: float, hz_min: float, hz_max: float, px_max: float) -> float:
        """Convert Hz to pixel position (using logarithmic scale)"""
        return math.log2(hz / hz_min) / math.log2(hz_max / hz_min) * px_max

    @staticmethod
    def px_to_hz(px: float, hz_min: float, hz_max: float, px_max: float) -> float:
        """Convert pixel position to hz (assuming pixel using logarithmic scale)"""
        c = px / px_max
        return hz_min ** (1 - c) * hz_max ** c  # type: ignore
