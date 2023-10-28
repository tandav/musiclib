import pytest
from musiclib.svg.isomorphic.squared import Squared
from musiclib.svg.isomorphic.hexagonal import Hexagonal


@pytest.mark.parametrize('cls', [Squared, Hexagonal])
def test_isomorphic(cls):
    cls()
