import collections
import dataclasses
import functools
import heapq
import itertools
import shutil
import sys
from pathlib import Path

import mido

from musictools import config
from musictools.chord import Chord
from musictools.chord import name_to_intervals
from musictools.chord import SpecificChord
from musictools.note import SpecificNote


def to_html():
    pass


def to_html_ul(l: list) -> str:
    li = '\n'.join(f'<li>{x}</li>' for x in l)
    return f'''
    <ul>
    {li}
    </ul>
    '''


@dataclasses.dataclass(frozen=True)
@functools.total_ordering
class MidiNote:
    note: SpecificNote
    on: int
    off: int
    track: int
    def __eq__(self, other): return self.on == other.on
    def __lt__(self, other): return self.on < other.on
    def __hash__(self): return hash((self.note, self.track))


def main():
    file = sys.argv[1]
    midi_dir = Path('logs') / Path(file).stem
    if midi_dir.exists():
        shutil.rmtree(midi_dir)
    midi_dir.mkdir()
    m = mido.MidiFile(file)

    notes = []

    index_list = []
    tracks = []

    for i, track in enumerate(m.tracks):
        trackname = f'{i}-{track.name}'
        index_list.append(f"<a href='{trackname}.html'>{trackname}</a>")
        track_list = []
        t = 0
        for message in track:
            t += message.time

            if message.type == 'control_change':
                continue

            d = message.dict()
            d.pop('channel', None)  # delete if exists
            d.pop('velocity', None)
            d['time'] = t
            if note_i := d.get('note'):
                d['note'] = str(SpecificNote.from_absolute_i(note_i))
                del d['time']

            ismeta = '<span class="meta_message">meta</span>' if message.is_meta else ''

            if message.type == 'note_on' and message.velocity == 0:  # https://stackoverflow.com/a/43322203/4204843
                message_type = 'note_off'
            else:
                message_type = message.type
            track_list.append(f"<code class='message'>{ismeta}</code> <code class='message_type_{message_type}'>{d}</code>")

        tracks.append(f'''
        <div class='track'>
        <h1><code>{trackname}</code></h1>
        {to_html_ul(track_list)}
        </div>
        ''')

    tracks = '\n'.join(tracks)

    html = f'''
    <h1><code>{file}</code></h1>
    <div class='tracks'>
    {tracks}
    </div>
    '''
    css = '''
    <style>
    body {
        background-color: rgba(0,0,0, 0.04);
    }
    .tracks {
        display: flex;
    }
    .track {
        background-color: white;
        margin: 10px;
        padding: 10px;
        border-radius: 3px;
        box-shadow: 2px 2px;
        border: 1px solid rgba(0,0,0,0.5);
    }
    li {
        white-space: nowrap;
        font-size: 8pt;
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
    with open(midi_dir / 'index.html', 'w') as index: index.write(html)


def parse_notes(m: mido.MidiFile) -> list[MidiNote]:
    notes = []
    for track_i, track in enumerate(m.tracks):
        t = 0
        t_buffer = dict()
        for message in track:
            t += message.time

            if message.type == 'note_on' and message.velocity != 0:
                t_buffer[message.note] = t

            elif message.type == 'note_off' or (message.type == 'note_on' and message.velocity == 0):  # https://stackoverflow.com/a/43322203/4204843
                heapq.heappush(notes, MidiNote(
                    note=SpecificNote.from_absolute_i(message.note),
                    on=t_buffer.pop(message.note), off=t,
                    track=track_i,
                ))
    return notes


def main2():
    file = sys.argv[1]
    midi_dir = Path('logs') / Path(file).stem
    if midi_dir.exists():
        shutil.rmtree(midi_dir)
    midi_dir.mkdir()
    m = mido.MidiFile(file)
    all_chords = [Chord.from_name(note, name) for note, name in itertools.product(config.chromatic_notes, name_to_intervals)]
    notes = parse_notes(m)
    tracks = [[] for track in m.tracks]
    harmony = []
    # prev = set()
    row = set()
    t = 0
    for i in range(len(notes)):
        note = heapq.heappop(notes)
        if note.on != t:

            # kinda printing
            print(len(row), row)

            abstract_notes = frozenset(n.note.abstract for n in row)
            harm = ''.join(n.name for n in abstract_notes)
            print(harm)
            for c in all_chords:
                # print(abstract_notes, c.notes)
                if c.notes == abstract_notes:
                    harm += f' | {c} {c.name}'
            harmony.append(f'<code>{harm}</code>')

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

    tracks2 = []
    tracks2.append(f'''
    <div class='track'>
    <h1 class='track_heading'><code>Harmony</code></h1>
    {to_html_ul(harmony)}
    </div>
    ''')

    for track_i, track in enumerate(tracks):
        tracks2.append(f'''
        <div class='track'>
        <h1 class='track_heading'><code>{track_i}-{m.tracks[track_i].name}</code></h1>
        {to_html_ul(track)}
        </div>
        ''')

    tracks = '\n'.join(tracks2)

    html = f'''
    <h1><code>{file}</code></h1>
    <div class='tracks'>
    {tracks}
    </div>
    '''
    css = '''
    <style>
    body {
        background-color: rgba(0,0,0, 0.04);
    }
    .tracks {
        display: flex;
    }
    .track {
        background-color: white;
        margin: 10px;
        padding: 10px;
        border-radius: 3px;
        box-shadow: 2px 2px;
        border: 1px solid rgba(0,0,0,0.5);
    }
    .track_heading {
        font-size: 8pt;
    }
    /**ul { list-style-type: none; }**/
    li {
        white-space: nowrap;
        font-size: 8pt;
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
    with open(midi_dir / 'index.html', 'w') as index: index.write(html)


if __name__ == '__main__':
    # main()
    main2()
