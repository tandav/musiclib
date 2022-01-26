import textwrap

import pytest

from musictool.chord import SpecificChord
from musictool.voice_leading.transition import Transition


@pytest.mark.parametrize('a, b, expected', (
    (
        'C3_E3_G3_C4',
        'B2_E3_G3_C4',
        '''\
        C3_E3_G3_C4
        /  |  |  |
        B2_E3_G3_C4''',
    ),
))
def test_transition(a, b, expected):
    assert repr(Transition(SpecificChord.from_str(a), SpecificChord.from_str(b))) == textwrap.dedent(expected)
