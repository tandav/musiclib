import mido
import shutil
import sys
from musictools.note import SpecificNote
from pathlib import Path


def to_html():
    pass


def to_html_ul(l: list) -> str:
    li = '\n'.join(f'<li>{x}</li>' for x in l)
    return f'''
    <ul>
    {li}
    </ul>
    '''

def main():
    file = sys.argv[1]
    midi_dir = Path('logs') / Path(file).stem
    if midi_dir.exists():
        shutil.rmtree(midi_dir)
    midi_dir.mkdir()
    m = mido.MidiFile(file)


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
            d.pop('channel', None) # delete if exists
            d.pop('velocity', None)
            d['time'] = t
            if note_i := d.get('note'):
                d['note'] = str(SpecificNote.from_absolute_i(note_i))

            ismeta = '<span class="meta_message">meta</span>' if message.is_meta else ''


            if message.type == 'note_on' and message.velocity == 0: # https://stackoverflow.com/a/43322203/4204843
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


if __name__ == '__main__':
    main()
