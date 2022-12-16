import itertools

import pytest
from colortool import Color

from musiclib.chord import Chord
from musiclib.chord import SpecificChord
from musiclib.noterange import NoteRange
from musiclib.noteset import NoteSet
from musiclib.scale import ComparedScales
from musiclib.scale import Scale
from musiclib.scale import all_scales

TITLE = 'title_fUYsZHfC'
SUBTITLE = 'subtitle_EfrKTj'
TITLE_HREF = 'title_href_TUMhv'
BACKGROUND_COLOR = Color.from_hex(0xFACE45)


def svg_helper(html, classes, title, subtitle, title_href, background_color):
    classes = ' '.join(classes)
    assert f'class="{classes}"' in html
    for item, constant in zip(
        (title, subtitle, title_href, background_color),
        (TITLE, SUBTITLE, TITLE_HREF, BACKGROUND_COLOR),
    ):
        if item is None:
            assert constant not in html
        elif isinstance(item, Color):
            assert item.css_hex in html
        else:
            if constant not in html:
                print(html)
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
@pytest.mark.parametrize('title_href', (None, TITLE_HREF))
@pytest.mark.parametrize('background_color', (BACKGROUND_COLOR,))
def test_html_noteset(noteset, title, subtitle, title_href, background_color):
    if title is None and title_href is not None:
        pytest.skip('title_href requires title')
    classes = ('cls1', 'cls2')
    svg = noteset._repr_svg_(
        classes=classes,
        title=title,
        subtitle=subtitle,
        title_href=title_href,
        background_color=background_color,
    )
    svg_helper(svg, classes, title, subtitle, title_href, background_color)


@pytest.mark.parametrize('kind', ('diatonic', 'harmonic', 'melodic', 'pentatonic', 'sudu'))
@pytest.mark.parametrize('title', (None, TITLE))
@pytest.mark.parametrize('subtitle', (None, SUBTITLE))
@pytest.mark.parametrize('title_href', (None, TITLE_HREF))
@pytest.mark.parametrize('background_color', (BACKGROUND_COLOR,))
def test_html_scale(kind, title, subtitle, title_href, background_color):
    if title is None and title_href is not None:
        pytest.skip('title_href requires title')
    for scale in all_scales[kind].values():
        classes = (scale.name,)
        svg = scale._repr_svg_(
            classes=classes,
            title=title,
            subtitle=subtitle,
            title_href=title_href,
            background_color=background_color,
        )
        svg_helper(svg, classes, title, subtitle, title_href, background_color)


@pytest.mark.parametrize(
    'scale0, scale1', (
        (Scale.from_name('C', 'major'), Scale.from_name('f', 'phrygian')),
        (Scale.from_name('A', 'major'), Scale.from_name('f', 'phrygian')),
    ),
)
@pytest.mark.parametrize('title', (None, TITLE))
@pytest.mark.parametrize('subtitle', (None, SUBTITLE))
@pytest.mark.parametrize('title_href', (None, TITLE_HREF))
@pytest.mark.parametrize('background_color', (BACKGROUND_COLOR,))
def test_html_compared_scale(scale0, scale1, title, subtitle, title_href, background_color):
    if title is None and title_href is not None:
        pytest.skip('title_href requires title')
    classes = ('cls1', 'cls2')
    svg = ComparedScales(scale0, scale1)._repr_svg_(
        classes=classes,
        title=title,
        subtitle=subtitle,
        title_href=title_href,
        background_color=background_color,
    )
    svg_helper(svg, classes, title, subtitle, title_href, background_color)


@pytest.mark.parametrize('root, name', itertools.product('Cf', Chord.name_to_intervals))
@pytest.mark.parametrize('title', (None, TITLE))
@pytest.mark.parametrize('subtitle', (None, SUBTITLE))
@pytest.mark.parametrize('title_href', (None, TITLE_HREF))
@pytest.mark.parametrize('background_color', (BACKGROUND_COLOR,))
def test_html_chord(root, name, title, subtitle, title_href, background_color):
    if title is None and title_href is not None:
        pytest.skip('title_href requires title')
    classes = ('cls1', 'cls2')
    svg = Chord.from_name(root, name)._repr_svg_(
        classes=classes,
        title=title,
        subtitle=subtitle,
        title_href=title_href,
        background_color=background_color,
    )
    svg_helper(svg, classes, title, subtitle, title_href, background_color)


@pytest.mark.parametrize(
    'chord', [
        SpecificChord.from_str('C1_E1_f1'),
        SpecificChord.from_str('C1_d3_A5'),
        SpecificChord(frozenset()),
    ],
)
@pytest.mark.parametrize('title', (None, TITLE))
@pytest.mark.parametrize('subtitle', (None, SUBTITLE))
@pytest.mark.parametrize('title_href', (None, TITLE_HREF))
@pytest.mark.parametrize('background_color', (BACKGROUND_COLOR,))
def test_html_specific_chord(chord, title, subtitle, title_href, background_color):
    if title is None and title_href is not None:
        pytest.skip('title_href requires title')
    classes = ('cls1', 'cls2')
    svg = chord._repr_svg_(
        classes=classes,
        title=title,
        subtitle=subtitle,
        title_href=title_href,
        background_color=background_color,
    )
    svg_helper(svg, classes, title, subtitle, title_href, background_color)


@pytest.mark.parametrize(
    'noterange', [
        NoteRange('C2', 'C5'),
        NoteRange('D2', 'G2', noteset=NoteSet.from_str('CDG')),
    ],
)
@pytest.mark.parametrize('title', (None, TITLE))
@pytest.mark.parametrize('subtitle', (None, SUBTITLE))
@pytest.mark.parametrize('title_href', (None, TITLE_HREF))
@pytest.mark.parametrize('background_color', (BACKGROUND_COLOR,))
def test_html_noterange(noterange, title, subtitle, title_href, background_color):
    if title is None and title_href is not None:
        pytest.skip('title_href requires title')
    classes = ('cls1', 'cls2')
    svg = noterange._repr_svg_(
        classes=classes,
        title=title,
        subtitle=subtitle,
        title_href=title_href,
        background_color=background_color,
    )
    svg_helper(svg, classes, title, subtitle, title_href, background_color)
