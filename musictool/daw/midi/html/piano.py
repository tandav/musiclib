import operator

import mido

from musictool import config
from musictool.daw.midi.parse.notes import parse_notes
from musictool.notes import note_range


# flake8: noqa
def midi_piano_html():
    file = config.MIDI_UI_FILE
    m = mido.MidiFile(file)
    notes = parse_notes(m)

    config.note_range = note_range(
        min(notes, key=operator.attrgetter('note')).note,
        max(notes, key=operator.attrgetter('note')).note,
    )
    print(config.note_range)
    width, height = 1600, 5000
    key_width = 5

    rects = []

    note_to_x = dict()
    for x, note in zip(range(0, width, key_width), config.note_range):
        note_to_x[note] = x
        if note.is_black:
            self.rects.append(f"""<rect x='{x}' y='0' width='{x + ww}' height='{self.size[1]}' style='fill:rgb{color};stroke-width:1;stroke:rgb{BLACK_COLOR}' onclick="play_note('{note.abstract.name}', '{note.octave}')"/>""")

            self.bg = imageutil.overlay_rect(self.bg, pt1=(x, 0), pt2=(x + key_width, config.frame_height), color=(0, 0, 0), alpha=0.5)
        else:
            thickness = 2 if note.abstract == 'B' else 1
            cv2.line(self.bg, (x + key_width, 0), (x + key_width, config.frame_height), (0, 0, 0, 255), thickness=thickness)

    if self.extra_note_space:
        extra_note, extra_space = self.extra_note_space
        x += key_width
        self.bg = imageutil.overlay_rect(self.bg, pt1=(x, 0), pt2=(x + extra_space, config.frame_height), color=(0, 0, 0), alpha=0.5)

    svg = f'''
    <svg width='{width}px' height='{height}px'>
    </svg>
    '''

    html = f'''
    {svg}
    '''

    css = '''
    <style>
    svg {
        background-color: rgba(0,0,0, 0.04);
    }
    </style>
    '''
    html += css
    return html
