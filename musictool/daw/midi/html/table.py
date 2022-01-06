import collections
import heapq
import itertools

import mido

from musictool import config
from musictool.chord import Chord
from musictool.daw.midi.parse.notes import parse_notes


def midi_table_html():
    file = config.MIDI_UI_FILE
    m = mido.MidiFile(file)
    m.tracks = m.tracks[::-1]  # specific for only test midi file (left -> right low -> high)
    all_chords = [Chord.from_name(note, name) for note, name in itertools.product(config.chromatic_notes, Chord.name_to_intervals)]
    notes = parse_notes(m)
    tracks = [[] for track in m.tracks]
    unique_notes = []
    harmony = []
    row = set()
    t = 0
    for i in range(len(notes)):
        note = heapq.heappop(notes)

        if note.on != t:

            # kinda printing
            print(len(row), row)

            abstract_notes = frozenset(n.note.abstract for n in row)
            unique_notes.append(f"<code>{''.join(n.name for n in abstract_notes)}</code>")
            harmony.append(
                f"<code>{' | '.join(f'{c} {c.name}' for c in all_chords if c.notes == abstract_notes)}</code>")

            _tn = collections.defaultdict(list)
            for n in row:
                _tn[n.track].append(n)

            for track_i, track in enumerate(tracks):
                if tn := _tn.get(track_i):
                    tn = sorted(tn, key=lambda n: n.note)
                    track.append(f"<code>{' '.join(str(n.note) for n in tn)}</code>")
                else:
                    track.append('')

            t = note.on
            row = set(n for n in row if t < n.off)
        row.add(note)

    assert len(set(map(len, tracks))) == 1

    tracks2 = []

    for row in zip(unique_notes, harmony, *tracks):
        row_line = '\n'.join(f'<td>{col}</td>' for col in row)
        tracks2.append(f'<tr>{row_line}</tr>')

    tracks = '\n'.join(tracks2)
    tracks_head = '\n'.join(f'<th><code>{i}-{track.name}</code></th>' for i, track in enumerate(m.tracks))
    tracks_head = '''
    <th><code>Unique Notes</code></th>
    <th><code>Harmony</code></th>
    ''' + tracks_head

    html = f'''
    <table>
    <caption><code>{file}</code></caption>
    <thead><tr>{tracks_head}</tr></thead>
    <tbody>
    {tracks}
    </tbody>
    </table>
    '''

    css = '''
    <style>
    body {
        background-color: rgba(0,0,0, 0.04);
    }
    code {
        font-size: 9pt;
    }

    table, th, td {
      border: 1px solid #dddddd;
      border-collapse: collapse;
    }

    th {
        writing-mode: vertical-lr;
        max-height: 100px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .track {
        background-color: white;
        margin: 10px;
        padding: 10px;
        border-radius: 3px;
        box-shadow: 2px 2px;
        border: 1px solid rgba(0,0,0,0.5);
    }
    .meta_message {
        background-color: #99CCFF;
    }
    .message_type_note_on {background-color: #76FF03;}
    .message_type_note_off {background-color: #FF5252;}
    /**code { font-family: Menlo, monospaced; }**/
    </style>
    '''
    html += css
    return html
