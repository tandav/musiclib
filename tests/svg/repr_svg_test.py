import itertools

import pytest
from colortool import Color
from musiclib import config
from musiclib.noteset import ComparedNoteSets
from musiclib.noteset import NoteSet
from musiclib.noteset import SpecificNoteSet
from musiclib.scale import Scale

TITLE = 'title_fUYsZHfC'
SUBTITLE = 'subtitle_EfrKTj'
TITLE_HREF = 'title_href_TUMhv'
BACKGROUND_COLOR = Color.from_hex(0xFACE45)
KINDS = 'natural', 'pentatonic', 'h_minor', 'h_major', 'm_minor'


@pytest.fixture
def all_scales():
    out = {}
    for kind in KINDS:
        out[kind] = {(root, name): Scale.from_name(root, name) for root, name in itertools.product(config.chromatic_notes, config.scale_order[kind])}
    return out


def svg_helper(html, classes, title, subtitle, title_href, background_color):
    classes = ' '.join(classes)
    assert f'class="{classes}"' in html
    for item, constant in zip(
        (title, subtitle, title_href, background_color),
        (TITLE, SUBTITLE, TITLE_HREF, BACKGROUND_COLOR),
        strict=True,
    ):
        if item is None:
            assert constant not in html
        elif isinstance(item, Color):
            assert item.css_hex in html
        else:
            if constant not in html:
                print(html)  # noqa: T201
            assert constant in html


@pytest.mark.parametrize(
    'noteset', [
        NoteSet.from_str('CdeFGa'),
        NoteSet.from_str('fa'),
        NoteSet.from_str(''),
    ],
)
@pytest.mark.parametrize('svg_method', ['svg_piano', 'svg_hex_piano'])
@pytest.mark.parametrize('title', [None, TITLE])
@pytest.mark.parametrize('subtitle', [None, SUBTITLE])
@pytest.mark.parametrize('title_href', [None, TITLE_HREF])
@pytest.mark.parametrize('background_color', [BACKGROUND_COLOR])
def test_svg_noteset(noteset, svg_method, title, subtitle, title_href, background_color):
    if title is None and title_href is not None:
        pytest.skip('title_href requires title')
    classes = ('cls1', 'cls2')
    svg = str(getattr(noteset, svg_method)(
        classes=classes,
        title=title,
        subtitle=subtitle,
        title_href=title_href,
        background_color=background_color,
    ))
    svg_helper(svg, classes, title, subtitle, title_href, background_color)


@pytest.mark.parametrize('kind', KINDS)
@pytest.mark.parametrize('svg_method', ['svg_piano', 'svg_hex_piano'])
@pytest.mark.parametrize('title', [None, TITLE])
@pytest.mark.parametrize('subtitle', [None, SUBTITLE])
@pytest.mark.parametrize('title_href', [None, TITLE_HREF])
@pytest.mark.parametrize('background_color', [BACKGROUND_COLOR])
def test_svg_scale(kind, svg_method, title, subtitle, title_href, background_color, all_scales):
    if title is None and title_href is not None:
        pytest.skip('title_href requires title')
    for scale in all_scales[kind].values():
        classes = tuple(scale.intervalset.names)
        svg = str(getattr(scale, svg_method)(
            classes=classes,
            title=title,
            subtitle=subtitle,
            title_href=title_href,
            background_color=background_color,
        ))
        svg_helper(svg, classes, title, subtitle, title_href, background_color)


@pytest.mark.parametrize(
    ('scale0', 'scale1'), [
        (Scale.from_name('C', 'major'), Scale.from_name('f', 'phrygian')),
        (Scale.from_name('A', 'major'), Scale.from_name('f', 'phrygian')),
    ],
)
@pytest.mark.parametrize('svg_method', ['svg_piano', 'svg_hex_piano'])
@pytest.mark.parametrize('title', [None, TITLE])
@pytest.mark.parametrize('subtitle', [None, SUBTITLE])
@pytest.mark.parametrize('title_href', [None, TITLE_HREF])
@pytest.mark.parametrize('background_color', [BACKGROUND_COLOR])
def test_svg_compared_notesets(scale0, scale1, svg_method, title, subtitle, title_href, background_color):
    if title is None and title_href is not None:
        pytest.skip('title_href requires title')
    classes = ('cls1', 'cls2')
    svg = str(getattr(ComparedNoteSets(scale0.noteset, scale1.noteset), svg_method)(
        classes=classes,
        title=title,
        subtitle=subtitle,
        title_href=title_href,
        background_color=background_color,
    ))
    svg_helper(svg, classes, title, subtitle, title_href, background_color)


@pytest.mark.parametrize(
    'sns', [
        SpecificNoteSet.from_str('C1_E1_f1'),
        SpecificNoteSet.from_str('C1_d3_A5'),
        SpecificNoteSet(frozenset()),
    ],
)
@pytest.mark.parametrize('svg_method', ['svg_piano', 'svg_hex_piano'])
@pytest.mark.parametrize('title', [None, TITLE])
@pytest.mark.parametrize('subtitle', [None, SUBTITLE])
@pytest.mark.parametrize('title_href', [None, TITLE_HREF])
@pytest.mark.parametrize('background_color', [BACKGROUND_COLOR])
def test_svg_specific_noteset(sns, svg_method, title, subtitle, title_href, background_color):
    if title is None and title_href is not None:
        pytest.skip('title_href requires title')
    classes = ('cls1', 'cls2')
    svg = str(getattr(sns, svg_method)(
        classes=classes,
        title=title,
        subtitle=subtitle,
        title_href=title_href,
        background_color=background_color,
    ))
    svg_helper(svg, classes, title, subtitle, title_href, background_color)
