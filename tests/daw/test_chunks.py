import io

from musictools import config
from musictools.daw import render
from musictools.midi.parse import parse_midi


def test_chunks():

    single = io.BytesIO()
    chunked = io.BytesIO()

    notes, song_samples = parse_midi(config.midi_file)
    render.single(single, notes, song_samples)

    notes, song_samples = parse_midi(config.midi_file)
    render.chunked(chunked, notes, song_samples)

    single = single.getvalue()
    chunked = chunked.getvalue()

    assert single == chunked
