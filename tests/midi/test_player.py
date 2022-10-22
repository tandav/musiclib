import os

import pytest

from musictool.midi.player import Player
from musictool.note import SpecificNote


@pytest.fixture
def player():
    return Player()


@pytest.mark.asyncio
async def test_specific_note(player, capsys):
    note = SpecificNote.from_i(60)
    await player.play(note, seconds=0.0001)
    stdout, stderr = capsys.readouterr()

    lines = [
        f'note_on note={note.i}, channel=0\n',
        f'note_off note={note.i}, channel=0\n',
    ]

    if 'MIDI_DEVICE' not in os.environ:
        lines = ['MIDI_DEVICE not found | ' + line for line in lines]

    assert stdout == ''.join(lines)
