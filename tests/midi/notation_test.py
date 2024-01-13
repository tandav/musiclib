import pytest

from musiclib.midi import notation
from musiclib.midi.notation import IntervalEvent



@pytest.mark.parametrize('code, name', [
    ('flute  1  2  3  4', 'flute'),
    ('bass                    9   8  -7  17   4 -12   0', 'bass'),
])
def test_voice_name(code, name):
    assert notation.Voice(code).name == name


@pytest.mark.parametrize('code, intervals', [
    (
        'flute  1  2  3  4',
        [
            IntervalEvent(interval=1, on=0, off=96),
            IntervalEvent(interval=2, on=96, off=192),
            IntervalEvent(interval=3, on=192, off=288),
            IntervalEvent(interval=4, on=288, off=384),
        ],
    ),
    (
        'flute  15 -3 .. -10 26 17 28 -- 17 29 -15  27  -8  -5  25  23',
        [
            IntervalEvent(interval=17, on=0, off=96),
            IntervalEvent(interval=-3, on=96, off=288),
            IntervalEvent(interval=-12, on=288, off=384),
            IntervalEvent(interval=30, on=384, off=480),
            IntervalEvent(interval=19, on=480, off=576),
            IntervalEvent(interval=32, on=576, off=768), 
            IntervalEvent(interval=19, on=768, off=864), 
            IntervalEvent(interval=33, on=864, off=960), 
            IntervalEvent(interval=-17, on=960, off=1056), 
            IntervalEvent(interval=31, on=1056, off=1152), 
            IntervalEvent(interval=-8, on=1152, off=1248), 
            IntervalEvent(interval=-5, on=1248, off=1344), 
            IntervalEvent(interval=29, on=1344, off=1440),
        ],
    ),
    # (
    #     'flute  16  5  24  15  0  7  -6  A  4  -15  -B  26  12  20  16  -11',
    #     [18, 5, 28, 17, 0, 7, -6, 10, 4, -17, -11, 30, 14, 24, 18, -13],
    # ),
    # (
    #     'flute  A   4 -15  -B  26  12  20  16 -11',
    #     [10, 4, -17, -11, 30, 14, 24, 18, -13],
    # ),
    # (
    #     'flute  15 -3 .. -10 26 17 28 .. 17 29 -15  27  -8  -5  25  23',
    #     [17, -3, None, -12, 30, 19, 32, None, 19, 33, -17, 31, -8, -5, 29, 27],
    # ),
    # (
    #     'bass    9   8  -7  17   4 -12   0  -6 -10  14  25   6  -3  13  -1  29',
    #     [9, 8, -7, 19, 4, -14, 0, -6, -12, 16, 29, 6, -3, 15, -1, 33],
    # ),
    # (
    #     'bass                    9   8  -7  17   4 -12   0  -6 -10  14  25   6  -3  13  -1  29',
    #     [9, 8, -7, 19, 4, -14, 0, -6, -12, 16, 29, 6, -3, 15, -1, 33],
    # ),
])
def test_voice(code, intervals):
    assert notation.Voice(code).intervals == intervals


code = '''\
header
version 2.2.1
intervalset major
root C1
ticks_per_beat 96

flute  13  29  13  26  22  22 -14   0  -1   4   2  19  11  27  -2   0
flute   4  -7  -8   7   5  18  18  23  26  24  12   3  -1  12 -13  17
piano  21  29   8  23  19   5  28  -8  26  16  -1   0  23  -7  27  25
bass    9   8  -7  17   4 -12   0  -6 -10  14  25   6  -3  13  -1  29

modulation
root A0
intervalset minor

flute  16   5  24  15   0   7  -6   7   4 -15   2  26  12  20  16 -11
flute  15  -3   0 -10  26  17  28  28  17  29 -15  27  -8  -5  25  23
piano   9  19 -11 -15  16  -8  12  -6  10   7  22  22  24  29  18  -4
bass  -13  28   7   5   8   1  16   9  -3 -11  -7  27   5   2   4  18

flutffsdfsdfsdf           16   5  24  15   0   7  -6   7   4 -15   2  26  12  20  16 -11
flutesdfsdfsd                 -3   0 -10  26  17  28  28  17  29 -15  27  -8  -5  25  23
pianosssssssssssssssssss   9  19 -11 -15  16  -8  12  -6  10   7  22  22  24  29  18  -4
bass                     -13  28   7   5   8   1  16   9  -3 -11  -7  27   5   2   4  18
'''


def test_notation():
    notation.Notation(code)
