import pytest

from musiclib.svg.isomorphic.hexagonal import Hexagonal
from musiclib.svg.isomorphic.squared import Squared


@pytest.mark.parametrize('cls', [Squared, Hexagonal])
def test_isomorphic(cls):
    cls()
