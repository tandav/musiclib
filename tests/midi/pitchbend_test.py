import pytest
from musiclib.midi.pitchbend import PitchPattern
from musiclib.midi.pitchbend import interpolate_pattern


@pytest.fixture
def pattern():
    return PitchPattern(time_bars=[0, 1 / 16, 1 / 16], pitch_st=[0, 2, 0])


@pytest.mark.parametrize(
    ('n_interp_points', 'expected'), [
        (0, ValueError),
        (3, ValueError),
        (
            4,
            PitchPattern(
                time_bars=(0.020833333333333332, 0, 0.0625, 0.0625),
                pitch_st=(0.6666666666666666, 0, 2, 0),
            ),
        ),
        (
            5,
            PitchPattern(
                time_bars=(0.015625, 0.03125, 0, 0.0625, 0.0625),
                pitch_st=(0.5, 1.0, 0, 2, 0),
            ),
        ),
        (
            9,
            PitchPattern(
                time_bars=(0.0078125, 0.015625, 0.0234375, 0.03125, 0.0390625, 0.046875, 0, 0.0625, 0.0625),
                pitch_st=(0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 0, 2, 0),
            ),
        ),
    ],
)
def test_interpolate_pattern(pattern, n_interp_points, expected):
    if isinstance(expected, type) and issubclass(expected, Exception):
        with pytest.raises(expected):
            interpolate_pattern(pattern, n_interp_points)
        return
    assert interpolate_pattern(pattern, n_interp_points) == expected
