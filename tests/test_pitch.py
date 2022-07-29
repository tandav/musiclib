import pytest

from musictool.pitch import Pitch


@pytest.mark.parametrize(
    'i, hz', [
        (-24, 110),
        (-12, 220),
        (0, 440),
        (1, 466.1637615180899),
        (2, 493.8833012561241),
        (12, 880),
    ],
)
def test_i_hz(i, hz):
    pitch = Pitch(hz_tuning=440)
    assert pitch.i_to_hz(i) == hz
    assert int(pitch.hz_to_i(hz)) == i


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
