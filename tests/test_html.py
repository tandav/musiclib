import itertools

import pytest

from musiclib.chord import Chord
from musiclib.chord import SpecificChord
from musiclib.noterange import NoteRange
from musiclib.noteset import NoteSet
from musiclib.scale import ComparedScales
from musiclib.scale import Scale
from musiclib.scale import all_scales

TITLE = 'title_fUYsZHfC'
SUBTITLE = 'subtitle_EfrKTj'
HEADER_HREF = 'header_href_TUMhv'
BACKGROUND_COLOR = '#FACE45'


def html_helper(html, html_classes, title, subtitle, header_href, background_color):
    classes = ' '.join(('card', *html_classes))
    assert f"class='{classes}'" in html
    for item, constant in zip(
        (title, subtitle, header_href, background_color),
        (TITLE, SUBTITLE, HEADER_HREF, BACKGROUND_COLOR),
    ):
        if item is None:
            assert constant not in html
        else:
            assert constant in html


@pytest.mark.parametrize(
    'noteset', [
        NoteSet.from_str('CdeFGa'),
        NoteSet.from_str('CdeFGa/e'),
        NoteSet.from_str('fa'),
        NoteSet.from_str('fa/f'),
        NoteSet.from_str(''),
    ],
)
@pytest.mark.parametrize('title', (None, TITLE))
@pytest.mark.parametrize('subtitle', (None, SUBTITLE))
@pytest.mark.parametrize('header_href', (None, HEADER_HREF))
@pytest.mark.parametrize('background_color', (None, BACKGROUND_COLOR))
def test_html_noteset(noteset, title, subtitle, header_href, background_color):
    html_classes = ('cls1', 'cls2')
    html = noteset._repr_html_(
        html_classes=html_classes,
        title=title,
        subtitle=subtitle,
        header_href=header_href,
        background_color=background_color,
    )
    html_helper(html, html_classes, title, subtitle, header_href, background_color)


@pytest.mark.parametrize('kind', ('diatonic', 'harmonic', 'melodic', 'pentatonic', 'sudu'))
@pytest.mark.parametrize('title', (None, TITLE))
@pytest.mark.parametrize('subtitle', (None, SUBTITLE))
@pytest.mark.parametrize('header_href', (None, HEADER_HREF))
@pytest.mark.parametrize('background_color', (None, BACKGROUND_COLOR))
def test_html_scale(kind, title, subtitle, header_href, background_color):
    for scale in all_scales[kind].values():
        html_classes = ('cls1', 'cls2')
        html = scale._repr_html_(
            html_classes=html_classes,
            title=title,
            subtitle=subtitle,
            header_href=header_href,
            background_color=background_color,
        )
        html_helper(html, html_classes + (scale.name,), title, subtitle, header_href, background_color)


@pytest.mark.parametrize(
    'scale0, scale1', (
        (Scale.from_name('C', 'major'), Scale.from_name('f', 'phrygian')),
        (Scale.from_name('A', 'major'), Scale.from_name('f', 'phrygian')),
    ),
)
@pytest.mark.parametrize('title', (None, TITLE))
@pytest.mark.parametrize('subtitle', (None, SUBTITLE))
@pytest.mark.parametrize('header_href', (None, HEADER_HREF))
@pytest.mark.parametrize('background_color', (None, BACKGROUND_COLOR))
def test_html_compared_scale(scale0, scale1, title, subtitle, header_href, background_color):
    html_classes = ('cls1', 'cls2')
    html = ComparedScales(scale0, scale1)._repr_html_(
        html_classes=html_classes,
        title=title,
        subtitle=subtitle,
        header_href=header_href,
        background_color=background_color,
    )
    html_helper(html, html_classes, title, subtitle, header_href, background_color)


@pytest.mark.parametrize('root, name', itertools.product('Cf', Chord.name_to_intervals))
@pytest.mark.parametrize('title', (None, TITLE))
@pytest.mark.parametrize('subtitle', (None, SUBTITLE))
@pytest.mark.parametrize('header_href', (None, HEADER_HREF))
@pytest.mark.parametrize('background_color', (None, BACKGROUND_COLOR))
def test_html_chord(root, name, title, subtitle, header_href, background_color):
    html_classes = ('cls1', 'cls2')
    html = Chord.from_name(root, name)._repr_html_(
        html_classes=html_classes,
        title=title,
        subtitle=subtitle,
        header_href=header_href,
        background_color=background_color,
    )
    html_helper(html, html_classes, title, subtitle, header_href, background_color)


@pytest.mark.parametrize(
    'chord', [
        SpecificChord.from_str('C1_E1_f1'),
        SpecificChord.from_str('C1_d3_A5'),
        SpecificChord(frozenset()),
    ],
)
@pytest.mark.parametrize('title', (None, TITLE))
@pytest.mark.parametrize('subtitle', (None, SUBTITLE))
@pytest.mark.parametrize('header_href', (None, HEADER_HREF))
@pytest.mark.parametrize('background_color', (None, BACKGROUND_COLOR))
def test_html_specific_chord(chord, title, subtitle, header_href, background_color):
    html_classes = ('cls1', 'cls2')
    html = chord._repr_html_(
        html_classes=html_classes,
        title=title,
        subtitle=subtitle,
        header_href=header_href,
        background_color=background_color,
    )
    html_helper(html, html_classes, title, subtitle, header_href, background_color)


@pytest.mark.parametrize(
    'noterange', [
        NoteRange('C2', 'C5'),
        NoteRange('D2', 'G2', noteset=NoteSet.from_str('CDG')),
    ],
)
@pytest.mark.parametrize('title', (None, TITLE))
@pytest.mark.parametrize('subtitle', (None, SUBTITLE))
@pytest.mark.parametrize('header_href', (None, HEADER_HREF))
@pytest.mark.parametrize('background_color', (None, BACKGROUND_COLOR))
def test_html_noterange(noterange, title, subtitle, header_href, background_color):
    html_classes = ('cls1', 'cls2')
    html = noterange._repr_html_(
        html_classes=html_classes,
        title=title,
        subtitle=subtitle,
        header_href=header_href,
        background_color=background_color,
    )
    html_helper(html, html_classes, title, subtitle, header_href, background_color)
