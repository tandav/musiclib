import math

from musictool.note import SpecificNote


class Pitch:
    def __init__(self, hz_tuning: float = 440, origin_note: SpecificNote = SpecificNote('A', 5)):
        self.hz_tuning = hz_tuning
        self.origin_note = origin_note

    def i_to_hz(self, i: float) -> float:
        return self.hz_tuning * 2 ** (i / 12)

    def hz_to_i(self, hz: float) -> float:
        return 12 * math.log2(hz / self.hz_tuning)

    def note_to_hz(self, note: SpecificNote) -> float:
        print(note.i - self.origin_note.i, note - self.origin_note)
        return self.i_to_hz(note.i - self.origin_note.i)

    @staticmethod
    def hz_to_px(hz: float, hz_min: float, hz_max: float, px_max: float) -> float:
        """Convert Hz to pixel position (using logarithmic scale)"""
        return math.log2(hz / hz_min) / math.log2(hz_max / hz_min) * px_max

    @staticmethod
    def px_to_hz(px: float, hz_min: float, hz_max: float, px_max: float) -> float:
        """Convert pixel position to hz (assuming pixel using logarithmic scale)"""
        c = px / px_max
        return hz_min ** (1 - c) * hz_max ** c  # type: ignore
