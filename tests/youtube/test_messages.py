from musictools.youtube.messages import parse_chords


def test_parse_chords():
    assert parse_chords('chords FACE') == 'FACE'
    assert parse_chords('chords fade') == 'fade'
    assert parse_chords('chords faDe') == 'faDe'
    assert parse_chords('chords FAcE') is None
    assert parse_chords('chords ') is None
    assert parse_chords('chords qwer') is None
    assert parse_chords('chords 12') is None
    assert parse_chords('fj4 12') is None
    assert parse_chords(' 234fj4 12') is None
    assert parse_chords('%') is None
    assert parse_chords('') is None
    assert parse_chords('     ') is None
    assert parse_chords('chords FACED') is None
