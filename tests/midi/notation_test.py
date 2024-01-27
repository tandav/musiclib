import json
from pathlib import Path

import musiclib
import pytest
import yaml
from musiclib.midi import notation
from musiclib.midi import parse

notation_examples = (p for p in (Path(__file__).parent / 'data/notation').iterdir() if p.is_dir())

@pytest.mark.parametrize('merge_voices', [False, True])
@pytest.mark.parametrize('example_dir', notation_examples)
def test_to_midi(example_dir, merge_voices):
    yaml_path = example_dir / 'code.yml'
    with open(yaml_path) as f:
        yaml_data = yaml.safe_load(f)
    yaml_data['musiclib_version'] = musiclib.__version__
    notation_ = notation.Notation.from_yaml_data(yaml_data)
    midifile = 'midi-merge-voices.json' if merge_voices else 'midi.json'
    with open(example_dir / midifile) as f:
        midi_dict = json.load(f)
    midi = notation_.to_midi(merge_voices=merge_voices)
    assert parse.to_dict(midi) == midi_dict
