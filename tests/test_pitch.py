import pytest

from musictool.note import SpecificNote
from musictool.pitch import Pitch

A4 = SpecificNote('A', 4)
A5 = SpecificNote('A', 5)
C5 = SpecificNote('C', 5)
HZ_220 = 220
HZ_440 = 440
HZ_493 = 493.8833012561241
HZ_261 = 261.6255653005986


@pytest.mark.parametrize(
    'i, hz', [
        (-24, 110),
        (-12, HZ_220),
        (-9, HZ_261),
        (0, 440),
        (1, 466.1637615180899),
        (2, HZ_493),
        (12, 880),
    ],
)
def test_i_hz(i, hz):
    pitch = Pitch(hz_tuning=HZ_440)
    assert pitch.i_to_hz(i) == hz
    assert int(pitch.hz_to_i(hz)) == i


@pytest.mark.parametrize(
    'hz_tuning, origin_note, i, hz', [
        (HZ_220, A5, 0, HZ_220),
        (HZ_220, A5, 12, HZ_440),
        (HZ_440, A4, 0, HZ_440),
        (HZ_440, A4, -12, HZ_220),
    ],
)
def test_tuning_origin_note(hz_tuning, origin_note, i, hz):
    pitch = Pitch(hz_tuning, origin_note)
    assert pitch.i_to_hz(i) == hz
    assert int(pitch.hz_to_i(hz)) == i


@pytest.mark.parametrize(
    'note, hz', [
        (A4, HZ_220),
        (A5, 440),
        (C5, HZ_261),
        (SpecificNote('B', 5), HZ_493),
        (SpecificNote('A', 6), 880),
    ],
)
def test_note_hz(note, hz):
    pitch = Pitch(HZ_440)
    assert pitch.note_to_hz(note) == hz
    assert pitch.hz_to_note(hz) == note


@pytest.mark.parametrize(
    'hz, px, hz_min, hz_max, px_max', [
        (55, 0, 55, 880, 1000),
        (110, 250, 55, 880, 1000),
        (220, 500, 55, 880, 1000),
        (440, 750, 55, 880, 1000),
        (880, 1000, 55, 880, 1000),
    ],
)
def test_hz_to_px(hz, px, hz_min, hz_max, px_max):
    assert Pitch.hz_to_px(hz, hz_min, hz_max, px_max) == pytest.approx(px)
    assert Pitch.px_to_hz(px, hz_min, hz_max, px_max) == pytest.approx(hz)
