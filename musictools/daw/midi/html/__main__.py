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

    template = string.Template(Path('static/midi-template.html').read_text())

    index_list = []

    for i, track in enumerate(m.tracks):
        trackname = f'{i}-{track.name}'
        index_list.append(f"<a href='{trackname}.html'>{trackname}</a>")
        track_list = []
        for message in track:
            d = {'is_meta': message.is_meta, **message.dict()}
            track_list.append(f'<code>{d}</code>')

        with open(midi_dir / f'{trackname}.html', 'w') as f:
            f.write(template.substitute(heading=f'{0} {track.name}', list=to_html_ul(track_list)))

    with open(midi_dir / 'index.html', 'w') as index:
        index.write(template.substitute(heading=file, list=to_html_ul(index_list)))


if __name__ == '__main__':
    main()
