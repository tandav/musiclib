import itertools

import pytest
from colortool import Color
from musiclib import config
from musiclib.noteset import NoteSet
from musiclib.noteset import SpecificNoteSet
from musiclib.scale import Scale
from musiclib.svg.pianoroll import PianoRoll

TITLE = 'title_fUYsZHfC'
SUBTITLE = 'subtitle_EfrKTj'
TITLE_HREF = 'title_href_TUMhv'
BACKGROUND_COLOR = Color.from_hex(0xFACE45)
KINDS = 'natural', 'm6'


@pytest.fixture
def all_scales():
    out = {}
    for kind in KINDS:
        out[kind] = {(root, name): Scale.from_name(root, name) for root, name in itertools.product(config.chromatic_notes, config.scale_order[kind])}
    return out


def svg_helper(svg, class_, title, subtitle, title_href, background_color):
    class_ = ' '.join(class_)
    assert f'class="{class_}"' in svg
    for item, constant in zip(
        (title, subtitle, title_href, background_color),
        (TITLE, SUBTITLE, TITLE_HREF, BACKGROUND_COLOR),
        strict=True,
    ):
        if item is None:
            assert constant not in svg
        elif isinstance(item, Color):
            assert item.css_hex in svg
        else:
            if constant not in svg:
                print(svg)  # noqa: T201
            assert constant in svg


def kw_helper(class_, title, subtitle, title_href, background_color, svg_method):
    kw = {
        'class_': class_,
        'header_kwargs': {
            'title': title,
            'subtitle': subtitle,
            'title_href': title_href,
        },
    }
    if svg_method == 'svg_piano':
        kw['background_color'] = background_color
    else:
        kw['header_kwargs']['background_color'] = background_color
    return kw


@pytest.mark.parametrize(
    'noteset', [
        NoteSet.from_str('CdeFGa'),
        NoteSet.from_str('fa'),
        NoteSet.from_str(''),
    ],
)
@pytest.mark.parametrize('svg_method', ['svg_piano', 'svg_plane_piano'])
@pytest.mark.parametrize('title', [None, TITLE])
@pytest.mark.parametrize('subtitle', [None, SUBTITLE])
@pytest.mark.parametrize('title_href', [None, TITLE_HREF])
@pytest.mark.parametrize('background_color', [BACKGROUND_COLOR])
def test_svg_noteset(noteset, svg_method, title, subtitle, title_href, background_color):
    if title is None and title_href is not None:
        pytest.skip('title_href requires title')
    class_ = ('cls1', 'cls2')
    kw = kw_helper(class_, title, subtitle, title_href, background_color, svg_method)
    svg = str(getattr(noteset, svg_method)(**kw))
    svg_helper(svg, class_, title, subtitle, title_href, background_color)


@pytest.mark.parametrize('kind', KINDS)
@pytest.mark.parametrize('svg_method', ['svg_piano', 'svg_plane_piano'])
@pytest.mark.parametrize('title', [None, TITLE])
@pytest.mark.parametrize('subtitle', [None, SUBTITLE])
@pytest.mark.parametrize('title_href', [None, TITLE_HREF])
@pytest.mark.parametrize('background_color', [BACKGROUND_COLOR])
def test_svg_scale(kind, svg_method, title, subtitle, title_href, background_color, all_scales):
    if title is None and title_href is not None:
        pytest.skip('title_href requires title')
    for scale in all_scales[kind].values():
        class_ = tuple(scale.intervalset.names)
        kw = kw_helper(class_, title, subtitle, title_href, background_color, svg_method)
        svg = str(getattr(scale, svg_method)(**kw))
        svg_helper(svg, class_, title, subtitle, title_href, background_color)


@pytest.mark.parametrize(
    'sns', [
        SpecificNoteSet.from_str('C1_E1_f1'),
        SpecificNoteSet.from_str('C1_d3_A5'),
        SpecificNoteSet(frozenset()),
    ],
)
@pytest.mark.parametrize('svg_method', ['svg_piano', 'svg_plane_piano'])
@pytest.mark.parametrize('title', [None, TITLE])
@pytest.mark.parametrize('subtitle', [None, SUBTITLE])
@pytest.mark.parametrize('title_href', [None, TITLE_HREF])
@pytest.mark.parametrize('background_color', [BACKGROUND_COLOR])
def test_svg_specific_noteset(sns, svg_method, title, subtitle, title_href, background_color):
    if title is None and title_href is not None:
        pytest.skip('title_href requires title')
    class_ = ('cls1', 'cls2')
    kw = kw_helper(class_, title, subtitle, title_href, background_color, svg_method)
    svg = str(getattr(sns, svg_method)(**kw))
    svg_helper(svg, class_, title, subtitle, title_href, background_color)


def test_repr_svg(midi):
    PianoRoll(midi)._repr_svg_()
