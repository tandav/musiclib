import io
import pickle

from musictools import config
from musictools.daw import render
from musictools.midi.parse import MidiTrack


def test_chunks():

    single = io.BytesIO()
    chunked = io.BytesIO()

    track = MidiTrack.from_file(config.midi_file)

    render.single(single, track)
    render.chunked(chunked, track)

    single = single.getvalue()
    chunked = chunked.getvalue()

    assert single == chunked
    with open('logs/log.pkl', 'wb') as f: pickle.dump(config.log, f)

