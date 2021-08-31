import functools
import itertools
from . import config, util
from .note import Note


class Piano:
    def __init__(self, size=None, scale=None, chord=None):
        if size is None:
            self.size = config.piano_img_size
        ww = self.size[0] // 14  # white key width
        bw = int(ww * 0.6)  # black key width

        white_notes = tuple(Note(config.chromatic_notes[i], octave) for octave, i in itertools.product((5, 6), (0, 2, 4, 5, 7, 9, 11)))
        black_notes = tuple(Note(config.chromatic_notes[i], octave) for octave, i in itertools.product((5, 6), (1, 3, 6, 8, 10)))

        WHITE_COLOR = (170,) * 3
        BLACK_COLOR = (80,) * 3
        for note in white_notes: note.color = WHITE_COLOR
        for note in black_notes: note.color = BLACK_COLOR

        self.rects = []

        for note, x in zip(white_notes, range(0, self.size[0], ww)):
            color = note.color
            note_no_octave = Note(note.name)
            if scale is not None and note_no_octave in scale.notes:
                color = scale.note_colors[note_no_octave]

            self.rects.append(f"""<rect x='{x}' y='0' width='{x + ww}' height='{self.size[1]}' style='fill:rgb{color};stroke-width:1;stroke:rgb{BLACK_COLOR}' onclick="play_note('{note.name}', '{note.octave}')"/>""")

        it = (x for i, x in enumerate(range(0 + ww, self.size[0], ww)) if i not in {2, 6, 9, 13})
        for note, x in zip(black_notes, it):
            color = note.color
            note_no_octave = Note(note.name)
            if scale is not None and note_no_octave in scale.notes:
                color = scale.note_colors[note_no_octave]
            self.rects.append(f"""<rect x='{x - bw // 2}', y='0' width='{bw}' height='{int(self.size[1] * 0.6)}' style='fill:rgb{color};stroke-width:1;stroke:rgb{BLACK_COLOR}' onclick="play_note('{note.name}', '{note.octave}')"/>""")

        self.rects.append(f"<rect x='0', y='0' width='{self.size[0] - 1}' height='{self.size[1] - 1}' style='fill:none;stroke-width:1;stroke:rgb{BLACK_COLOR}'/>")

    def __repr__(self):
        return 'Piano'

    def _repr_svg_(self):
        rects = '\n'.join(self.rects)
        return f'''
        <svg width='{self.size[0]}' height='{self.size[1]}'>
        {rects}
        </svg>
        '''

