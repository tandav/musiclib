import dataclasses
import functools

import mido

from musiclib.note import SpecificNote


@dataclasses.dataclass(frozen=True)
@functools.total_ordering
class MidiNote:
    note: SpecificNote
    on: int
    off: int
    track: int

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MidiNote):
            return NotImplemented
        return self.on == other.on

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, MidiNote):
            return NotImplemented
        return self.on < other.on

    def __hash__(self) -> int:
        return hash((self.note, self.track))


def parse_notes(m: mido.MidiFile) -> list[MidiNote]:
    notes: list[MidiNote] = []
    for track_i, track in enumerate(m.tracks):
        t = 0
        t_buffer = {}
        for message in track:
            t += message.time

            if message.type == 'note_on' and message.velocity != 0:
                t_buffer[message.note] = t

            elif message.type == 'note_off' or (
                message.type == 'note_on' and message.velocity == 0
            ):  # https://stackoverflow.com/a/43322203/4204843
                # TODO: heapq seems unnecessary here
                # heapq.heappush(
                # notes, MidiNote(
                #     note=SpecificNote.from_i(message.note),
                #     on=t_buffer.pop(message.note),
                #     off=t,
                #     track=track_i,
                # ),
                # )
                notes.append(
                    MidiNote(
                        note=SpecificNote.from_i(message.note),
                        on=t_buffer.pop(message.note),
                        off=t,
                        track=track_i,
                    ),
                )
    return notes
