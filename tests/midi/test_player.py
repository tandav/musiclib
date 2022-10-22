import os

import pytest

from musictool.chord import SpecificChord
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


@pytest.mark.asyncio
async def test_specific_chord(player, capsys):
    await player.play(SpecificChord.from_str('C1_E1_G2'), seconds=0.0001)
    stdout, stderr = capsys.readouterr()
    stdout_ = []
    prefix = 'MIDI_DEVICE not found | '
    for line in stdout.splitlines():
        assert line.startswith(prefix)
        stdout_.append(line.removeprefix(prefix))
    on, off = set(stdout_[:3]), set(stdout_[3:])
    assert on == {'note_on note=12, channel=0', 'note_on note=16, channel=0', 'note_on note=31, channel=0'}
    assert off == {'note_off note=12, channel=0', 'note_off note=16, channel=0', 'note_off note=31, channel=0'}
