import pytest
from musiclib.note import SpecificNote
from musiclib.pitch import Pitch

A3 = SpecificNote('A', 3)
A4 = SpecificNote('A', 4)
A5 = SpecificNote('A', 5)
A6 = SpecificNote('A', 6)
B4 = SpecificNote('B', 4)
b4 = SpecificNote('b', 4)
C4 = SpecificNote('C', 4)
HZ_220 = 220
HZ_440 = 440
HZ_880 = 880
HZ_493 = 493.8833012561241
HZ_452 = 452.8929841231365
HZ_466 = 466.1637615180899
HZ_261 = 261.6255653005986


@pytest.mark.parametrize(
    ('x', 's', 'r'), [
        (
            Pitch(),
            "Pitch(hz_tuning=440, origin_note=SpecificNote('A', 4))",
            "Pitch(hz_tuning=440, origin_note=SpecificNote('A', 4))",
        ),
    ],
)
def test_str_repr(x, s, r):
    assert str(x) == s
    assert repr(x) == r


@pytest.mark.parametrize(
    ('i', 'hz'), [
        (A3.i, HZ_220),
        (C4.i, HZ_261),
        (A4.i, HZ_440),
        (b4.i, HZ_466),
        (B4.i, HZ_493),
        (A5.i, HZ_880),
    ],
)
def test_i_hz(i, hz):
    pitch = Pitch()
    assert pitch.i_to_hz(i) == hz
    assert int(pitch.hz_to_i(hz)) == i


@pytest.mark.parametrize(
    ('hz', 'note'), [
        (441, A4),
        (452.9, b4),
        (465, b4),
    ],
)
def test_round(hz, note):
    pitch = Pitch()
    assert pitch.hz_to_note(hz) == note


@pytest.mark.parametrize(
    ('hz_tuning', 'origin_note', 'i', 'hz'), [
        (HZ_220, A5, A5.i, HZ_220),
        (HZ_220, A5, A6.i, HZ_440),
        (HZ_440, A4, A4.i, HZ_440),
        (HZ_440, A4, A3.i, HZ_220),
    ],
)
def test_tuning_origin_note(hz_tuning, origin_note, i, hz):
    pitch = Pitch(hz_tuning, origin_note)
    assert pitch.i_to_hz(i) == hz
    assert int(pitch.hz_to_i(hz)) == i


@pytest.mark.parametrize(
    ('note', 'hz'), [
        (A3, HZ_220),
        (A4, HZ_440),
        (A5, HZ_880),
        (C4, HZ_261),
        (B4, HZ_493),
    ],
)
def test_note_hz(note, hz):
    pitch = Pitch()
    assert pitch.note_to_hz(note) == hz
    assert pitch.hz_to_note(hz) == note


@pytest.mark.parametrize(
    ('hz', 'px', 'hz_min', 'hz_max', 'px_max'), [
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
