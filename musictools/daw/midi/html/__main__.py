import mido
import shutil
import sys
import string
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
            d = {'is_meta': message.is_meta, **message.dict()}
            d['time'] = t
            track_list.append(f"<code class='message'>{d}</code>")

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
    .message {
        white-space: nowrap;
    }

    </style>
    '''
    html += css
    with open(midi_dir / 'index.html', 'w') as index: index.write(html)


if __name__ == '__main__':
    main()
