import pytest

from musictool.note import SpecificNote
from musictool.pitch import Pitch

A4 = SpecificNote('A', 4)
A5 = SpecificNote('A', 5)
A6 = SpecificNote('A', 6)
B5 = SpecificNote('B', 5)
b5 = SpecificNote('b', 5)
C5 = SpecificNote('C', 5)
HZ_220 = 220
HZ_440 = 440
HZ_880 = 880
HZ_493 = 493.8833012561241
HZ_452 = 452.8929841231365
HZ_466 = 466.1637615180899
HZ_261 = 261.6255653005986


@pytest.mark.parametrize(
    'i, hz', [
        (-24, 110),
        (-12, HZ_220),
        (-9, HZ_261),
        (0, HZ_440),
        (1, HZ_466),
        (2, HZ_493),
        (12, HZ_880),
    ],
)
def test_i_hz(i, hz):
    pitch = Pitch()
    assert pitch.i_to_hz(i) == hz
    assert int(pitch.hz_to_i(hz)) == i


@pytest.mark.parametrize(
    'note_i, hz', [
        (A5.i, HZ_440),
        (b5.i, HZ_466),
        (A4.i, HZ_220),
        (C5.i, HZ_261),
        (A5.i + 0.5, HZ_452),
    ],
)
def test_note_i_hz(note_i, hz):
    pitch = Pitch()
    assert pitch.note_i_to_hz(note_i) == hz
    assert pitch.hz_to_note_i(hz) == note_i


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
        (B5, HZ_493),
        (A6, HZ_880),
    ],
)
def test_note_hz(note, hz):
    pitch = Pitch()
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


@pytest.mark.parametrize(
    'note, transpose, hz', [
        (A5, -12, HZ_220),
        (A5, +12, HZ_880),
        (A5, +1, HZ_466),
        (A5, +0.5, HZ_452),
    ],
)
def test_transpose(note, transpose, hz):
    pitch = Pitch(transpose=transpose)
    assert pitch.note_to_hz(note) == hz
    assert pitch.hz_to_note(hz) == note
