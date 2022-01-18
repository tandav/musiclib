import pytest

from musictool.voice_leading import progression


@pytest.mark.xfail(reason='deprecated')
def test_count_all_triads():
    assert len(progression.all_triads()) == 972
