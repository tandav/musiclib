import pytest
from musiclib.midi.player import Player
from musiclib.note import SpecificNote
from musiclib.noteset import SpecificNoteSet


@pytest.fixture
def player():
    return Player()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ('note_i', 'channel', 'velocity'), [
        (60, 0, 100),
        (64, 1, 3),
    ],
)
async def test_specific_note(note_i, channel, velocity, player, capsys):
    note = SpecificNote.from_i(note_i)
    await player.play(note, seconds=0.0001, channel=channel, velocity=velocity)
    stdout, stderr = capsys.readouterr()
    lines = [
        f'note_on channel={channel} note={note_i} velocity={velocity} time=0',
        f'note_off channel={channel} note={note_i} velocity={velocity} time=0',
    ]
    lines = [f'MIDI_DEVICE not found | {line}\n' for line in lines]
    assert stdout == ''.join(lines)


@pytest.mark.asyncio
async def test_specific_chord(player, capsys):
    await player.play(SpecificNoteSet.from_str('C1_E1_G2'), seconds=0.0001)
    stdout, stderr = capsys.readouterr()
    stdout_ = []
    prefix = 'MIDI_DEVICE not found | '
    for line in stdout.splitlines():
        assert line.startswith(prefix)
        stdout_.append(line.removeprefix(prefix))
    on, off = set(stdout_[:3]), set(stdout_[3:])
    assert on == {
        'note_on channel=0 note=24 velocity=100 time=0',
        'note_on channel=0 note=28 velocity=100 time=0',
        'note_on channel=0 note=43 velocity=100 time=0',
    }
    assert off == {
        'note_off channel=0 note=24 velocity=100 time=0',
        'note_off channel=0 note=28 velocity=100 time=0',
        'note_off channel=0 note=43 velocity=100 time=0',
    }
