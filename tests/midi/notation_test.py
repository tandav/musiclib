import json
from pathlib import Path

import musiclib
import pytest
import yaml
from musiclib.midi import notation
from musiclib.midi import parse
# from musiclib.midi.notation import IntervalEvent


# @pytest.mark.parametrize(
#     ('intervals_str', 'interval_events'), [
#         (
#             '1  2  3  4',
#             [
#                 IntervalEvent(interval=1, on=0, off=96),
#                 IntervalEvent(interval=2, on=96, off=192),
#                 IntervalEvent(interval=3, on=192, off=288),
#                 IntervalEvent(interval=4, on=288, off=384),
#             ],
#         ),
#         (
#             '15 -3 .. -10 26 17 28 -- 17 29 -15  27  -8  -5  25  23',
#             [
#                 IntervalEvent(interval=17, on=0, off=96),
#                 IntervalEvent(interval=-3, on=96, off=288),
#                 IntervalEvent(interval=-12, on=288, off=384),
#                 IntervalEvent(interval=30, on=384, off=480),
#                 IntervalEvent(interval=19, on=480, off=576),
#                 IntervalEvent(interval=32, on=576, off=768),
#                 IntervalEvent(interval=19, on=768, off=864),
#                 IntervalEvent(interval=33, on=864, off=960),
#                 IntervalEvent(interval=-17, on=960, off=1056),
#                 IntervalEvent(interval=31, on=1056, off=1152),
#                 IntervalEvent(interval=-8, on=1152, off=1248),
#                 IntervalEvent(interval=-5, on=1248, off=1344),
#                 IntervalEvent(interval=29, on=1344, off=1440),
#                 IntervalEvent(interval=27, on=1440, off=1536),
#             ],
#         ),
#     ],
# )
# def test_voice(intervals_str, interval_events):
#     assert notation.Voice.from_intervals_str(channel='flute', intervals_str=intervals_str).interval_events == interval_events


notation_examples = (p for p in (Path(__file__).parent / 'data/notation').iterdir() if p.is_dir())

notation_examples = list(notation_examples)[:1]

@pytest.mark.parametrize('example_dir', notation_examples)
def test_to_midi(example_dir):
    yaml_path = example_dir / 'code.yml'
    with open(yaml_path) as f:
        yaml_data = yaml.safe_load(f)
    yaml_data['musiclib_version'] = musiclib.__version__
    notation_ = notation.Notation.from_yaml_data(yaml_data)
    with open(example_dir / 'midi.json') as f:
        midi_dict = json.load(f)
    assert parse.to_dict(notation_.to_midi()) == midi_dict
