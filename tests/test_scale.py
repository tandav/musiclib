import operator

import pytest

from musictool import config
from musictool.chord import Chord
from musictool.note import Note
from musictool.scale import ComparedScales
from musictool.scale import Scale
from musictool.scale import all_scales


@pytest.mark.parametrize(
    'notes, name', (
        ('CDEFGAB', 'major'),
        ('CdeFGab', 'phrygian'),
        ('DEFGAbC', 'minor'),
        ('bdefa', 'p_phrygian'),
    ),
)
def test_name(notes, name):
    root = notes[0]
    notes = frozenset(notes)
    assert Scale(notes, root=root).name == name
    assert Scale.from_name(root, name).notes == notes


def test_kind():
    s = Scale.from_name('C', 'major')
    assert (
        s.kind == 'diatonic' and
        {'note_scales', 'triads', 'sevenths', 'ninths', 'notes_to_triad_root'} <= vars(s).keys()
    )
    s = Scale.from_name('C', 'p_major')
    assert (
        s.kind == 'pentatonic' and
        {'note_scales'} <= vars(s).keys() and
        len({'triads', 'sevenths', 'ninths', 'notes_to_triad_root'} & vars(s).keys()) == 0
    )


@pytest.mark.parametrize(
    'op, a, b', (
        (operator.eq, Scale.from_name('C', 'major'), Scale.from_name('C', 'major')),
        (operator.eq, Scale.from_name('C', 'major'), Scale.from_name(Note('C'), 'major')),
        (operator.eq, Scale.from_name(Note('C'), 'major'), Scale.from_name(Note('C'), 'major')),
        (operator.ne, Scale.from_name(Note('C'), 'major'), Scale.from_name(Note('E'), 'major')),
    ),
)
def test_equal(op, a, b):
    assert op(a, b)


@pytest.mark.parametrize(
    'notes, name, nths', (
        ('CDEFGAB', 'triads', 'CEG/C DFA/D EGB/E FAC/F GBD/G ACE/A BDF/B'),
        ('DEFGAbC', 'triads', 'DFA/D EGb/E FAC/F GbD/G ACE/A bDF/b CEG/C'),
        ('CDEFGAB', 'sevenths', 'CEGB/C DFAC/D EGBD/E FACE/F GBDF/G ACEG/A BDFA/B'),
        ('DEFGAbC', 'sevenths', 'DFAC/D EGbD/E FACE/F GbDF/G ACEG/A bDFA/b CEGb/C'),
        ('CDEFGAB', 'ninths', 'CEGBD/C DFACE/D EGBDF/E FACEG/F GBDFA/G ACEGB/A BDFAC/B'),
        ('DEFGAbC', 'ninths', 'DFACE/D EGbDF/E FACEG/F GbDFA/G ACEGb/A bDFAC/b CEGbD/C'),
    ),
)
def test_nths(notes, name, nths):
    assert getattr(Scale(frozenset(notes), root=notes[0]), name) == tuple(Chord.from_str(s) for s in nths.split())


def test_notes_to_triad_root():
    assert Scale(frozenset('DEFGAbC'), root='D').notes_to_triad_root[frozenset(map(Note, 'GbD'))] == 'G'


@pytest.mark.parametrize('notes', ('CDEFGAB', 'BdeEfab', 'deFfabC'))
def test_note_scales(notes):
    assert Scale(frozenset(notes), root=notes[0]).note_scales == dict(zip(notes, config.diatonic, strict=True))


def test_compared():
    left = Scale.from_name('C', 'major')
    right = Scale.from_name('A', 'minor')
    assert ComparedScales(left, right).shared_notes == frozenset(left.notes)

    right = Scale.from_name('C', 'mixolydian')
    c = ComparedScales(left, right)
    assert c.new_notes == frozenset({Note('b')})
    assert c.del_notes == frozenset({Note('B')})


@pytest.mark.parametrize(
    'scale, parallel_name, expected', (
        (Scale.from_name('C', 'major'), 'minor', Scale.from_name('C', 'minor')),
        (Scale.from_name('C', 'minor'), 'major', Scale.from_name('C', 'major')),
        (Scale.from_name('f', 'minor'), 'major', Scale.from_name('f', 'major')),
        (Scale.from_name('C', 'major'), 'phrygian', Scale.from_name('C', 'phrygian')),
        (Scale.from_name('e', 'dorian'), 'locrian', Scale.from_name('e', 'locrian')),
    ),
)
def test_parallel(scale, parallel_name, expected):
    assert scale.parallel(parallel_name) is expected


@pytest.mark.parametrize(
    'scale, relative_name, expected', (
        (Scale.from_name('C', 'major'), 'minor', Scale.from_name('A', 'minor')),
        (Scale.from_name('A', 'minor'), 'major', Scale.from_name('C', 'major')),
        (Scale.from_name('f', 'minor'), 'major', Scale.from_name('A', 'major')),
        (Scale.from_name('A', 'major'), 'minor', Scale.from_name('f', 'minor')),
        (Scale.from_name('C', 'major'), 'phrygian', Scale.from_name('E', 'phrygian')),
        (Scale.from_name('A', 'major'), 'dorian', Scale.from_name('B', 'dorian')),
    ),
)
def test_relative(scale, relative_name, expected):
    assert scale.relative(relative_name) is expected


TITLE = 'title_fUYsZHfC'
SUBTITLE = 'subtitle_EfrKTj'
HEADER_HREF = 'header_href_TUMhv'


@pytest.mark.parametrize('kind', ('diatonic', 'harmonic', 'melodic', 'pentatonic', 'sudu'))
@pytest.mark.parametrize('title', (None, TITLE))
@pytest.mark.parametrize('subtitle', (None, SUBTITLE))
@pytest.mark.parametrize('header_href', (None, HEADER_HREF))
def test_html(kind, title, subtitle, header_href):
    for scale in all_scales[kind].values():
        html_classes = ('cls1', 'cls2')
        html = scale._repr_html_(
            html_classes=html_classes,
            title=title,
            subtitle=subtitle,
            header_href=header_href,
        )
        classes = ' '.join(['card', *html_classes, scale.name])
        assert f"class='{classes}'" in html
        for item, constant in zip(
            (title, subtitle, header_href),
            (TITLE, SUBTITLE, HEADER_HREF),
        ):
            if item is None:
                assert constant not in html
            else:
                assert constant in html


@pytest.mark.parametrize(
    'scale0, scale1', (
        (Scale.from_name('C', 'major'), Scale.from_name('f', 'phrygian')),
        (Scale.from_name('A', 'major'), Scale.from_name('f', 'phrygian')),
    ),
)
@pytest.mark.parametrize('title', (None, TITLE))
@pytest.mark.parametrize('subtitle', (None, SUBTITLE))
@pytest.mark.parametrize('header_href', (None, HEADER_HREF))
def test_html_compared_scale(scale0, scale1, title, subtitle, header_href):
    html_classes = ('cls1', 'cls2')
    html = ComparedScales(scale0, scale1)._repr_html_(
        html_classes=html_classes,
        title=title,
        subtitle=subtitle,
        header_href=header_href,
    )
    classes = ' '.join(['card', *html_classes])
    assert f"class='{classes}'" in html

    for item, constant in zip(
        (title, subtitle, header_href),
        (TITLE, SUBTITLE, HEADER_HREF),
    ):
        if item is None:
            assert constant not in html
        else:
            assert constant in html
