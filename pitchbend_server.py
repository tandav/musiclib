from pathlib import Path

import mido
from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from musiclib.midi import parse
from musiclib.midi.pitchbend import PitchPattern
from musiclib.noterange import NoteRange
from musiclib.svg.pianoroll import PianoRoll
from starlette.templating import Jinja2Templates

static_folder = Path('static')

app = FastAPI()
app.mount('/static/', StaticFiles(directory=static_folder), name='static')
templates = Jinja2Templates(directory=static_folder / 'templates')


patterns = [
    PitchPattern(time_bars=[0, 1 / 16, 1 / 16], pitch_st=[0, 2, 0]),
    PitchPattern(time_bars=[0, 1 / 16, 1 / 16], pitch_st=[0, -2, 0]),
]


@app.get('/', response_class=HTMLResponse)
async def get_pianoroll(
    request: Request,
    pitchbend_semitones: int = 2,
    noterange: str = 'C3-C5',
    selected_note: str | None = None,
):
    # MIDI_PATH = '/Users/tandav/docs/bhairava/pieces-of-music/midi/PB-simple-overlap.mid'
    MIDI_PATH = '/Users/tandav/docs/bhairava/pieces-of-music/midi/pitchbend/basic.mid'
    midi = mido.MidiFile(MIDI_PATH)
    midi = parse.parse_midi(midi)
    noterange = NoteRange(*noterange.split('-'))
    pianoroll = PianoRoll(
        midi=midi,
        noterange=noterange,
        pitchbend_semitones=2,
    )
    return templates.TemplateResponse(
        'pitchbend.j2', {
            'request': request,
            'pianoroll': pianoroll._repr_svg_(),
        },
    )
