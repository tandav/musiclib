import pytest

from piano_scales import voice_leading


@pytest.mark.xfail(reason='deprecated')
def test_count_all_triads():
    assert len(voice_leading.all_triads()) == 972
