import pytest
from musiclib.svg.isomorphic import Square
from musiclib.svg.isomorphic import Hex


@pytest.mark.parametrize('cls', [Square, Hex])
def test_isomorphic(cls):
    cls()
