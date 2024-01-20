import json
from pathlib import Path

import pytest
from musiclib.midi import notation
from musiclib.midi import parse
from musiclib.midi.notation import IntervalEvent


@pytest.mark.parametrize(
    ('code', 'channel'), [
        ('flute  1  2  3  4', 'flute'),
        ('bass                    9   8  -7  17   4 -12   0', 'bass'),
    ],
)
def test_voice_channel(code, channel):
    assert notation.Voice(code).channel == channel


@pytest.mark.parametrize(
    ('code', 'interval_events'), [
        (
            'flute  1  2  3  4',
            [
                IntervalEvent(interval=1, on=0, off=96),
                IntervalEvent(interval=2, on=96, off=192),
                IntervalEvent(interval=3, on=192, off=288),
                IntervalEvent(interval=4, on=288, off=384),
            ],
        ),
        (
            'flute  15 -3 .. -10 26 17 28 -- 17 29 -15  27  -8  -5  25  23',
            [
                IntervalEvent(interval=17, on=0, off=96),
                IntervalEvent(interval=-3, on=96, off=288),
                IntervalEvent(interval=-12, on=288, off=384),
                IntervalEvent(interval=30, on=384, off=480),
                IntervalEvent(interval=19, on=480, off=576),
                IntervalEvent(interval=32, on=576, off=768),
                IntervalEvent(interval=19, on=768, off=864),
                IntervalEvent(interval=33, on=864, off=960),
                IntervalEvent(interval=-17, on=960, off=1056),
                IntervalEvent(interval=31, on=1056, off=1152),
                IntervalEvent(interval=-8, on=1152, off=1248),
                IntervalEvent(interval=-5, on=1248, off=1344),
                IntervalEvent(interval=29, on=1344, off=1440),
                IntervalEvent(interval=27, on=1440, off=1536),
            ],
        ),
    ],
)
def test_voice(code, interval_events):
    assert notation.Voice(code).interval_events == interval_events


@pytest.mark.parametrize('example_dir', (Path(__file__).parent / 'data/notation').iterdir())
def test_to_midi(example_dir):
    code = (example_dir / 'code.txt').read_text()
    with open(example_dir / 'midi.json') as f:
        midi_dict = json.load(f)
    assert parse.to_dict(notation.Notation(code).to_midi()) == midi_dict
