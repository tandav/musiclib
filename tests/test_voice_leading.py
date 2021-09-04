from piano_scales import voice_leading


def test_count_all_triads():
    assert len(voice_leading.all_triads()) == 972
