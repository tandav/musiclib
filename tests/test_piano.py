import collections
from xml.etree import ElementTree

import pytest
from colortool import Color

from musiclib import config
from musiclib.note import Note
from musiclib.note import SpecificNote
from musiclib.noterange import NoteRange
from musiclib.piano import Piano
from musiclib.piano import note_color


@pytest.mark.parametrize(
    'note, color', [
        (Note('C'), config.WHITE_PALE),
        (Note('d'), config.BLACK_PALE),
        (SpecificNote('C', 1), config.WHITE_PALE),
        (SpecificNote('d', 1), config.BLACK_PALE),
    ],
)
def test_note_color(note, color):
    assert note_color(note) == color


def note_info(svg: str, element: str, class_: str) -> dict[SpecificNote, dict[str, str | Color]]:
    """
    element: rect | text | g
    info_part be fill | stroke | text | text_color | onclick
    """
    out: dict[SpecificNote, dict[str, str | Color]] = collections.defaultdict(dict)
    svg = svg.replace('xmlns="http://www.w3.org/2000/svg"', '')  # ElementTree findall dont work with xmlns
    for r in ElementTree.fromstring(svg).findall(f'.//{element}/[@class]'):
        if not r.attrib['class'].startswith(class_):
            continue
        note = SpecificNote.from_str(r.attrib['class'].split()[1])
        if fill := r.attrib.get('fill'):
            out[note]['fill'] = Color.from_css_hex(fill)
        if stroke := r.attrib.get('stroke'):
            out[note]['stroke'] = Color.from_css_hex(stroke)
        if text := r.text:
            out[note]['text'] = text
        if onclick := r.attrib.get('onclick'):
            out[note]['onclick'] = onclick
    return dict(out)


@pytest.mark.parametrize(
    'notes', [
        (Note('C'), SpecificNote('C', 0), SpecificNote('C', 1)),
        (Note('d'), SpecificNote('d', 0), SpecificNote('d', 1)),
    ],
)
@pytest.mark.parametrize(
    'element, class_, info_part, keyarg, payload, expected', [
        ('rect', 'note', 'fill', 'note_colors', config.RED, config.RED),
        ('rect', 'top_rect', 'fill', 'top_rect_colors', config.RED, config.RED),
        ('rect', 'square', 'fill', 'squares', {'fill_color': config.RED}, config.RED),
        ('rect', 'square', 'stroke', 'squares', {'border_color': config.RED}, config.RED),
        ('text', 'square', 'fill', 'squares', {'text': 'T', 'text_color': config.RED}, config.RED),
        ('text', 'square', 'text', 'squares', {'text': 'T'}, 'T'),
        ('g', 'square', 'onclick', 'squares', {'onclick': 'T'}, 'T'),
    ],
)
@pytest.mark.parametrize('black_small', [True, False])
def test_abstract(element, class_, info_part, keyarg, payload, expected, notes, black_small):
    svg = Piano(**{keyarg: {notes[0]: payload}}, black_small=black_small)._repr_svg_()  # type: ignore
    i = note_info(svg, element, class_)
    assert i[notes[1]][info_part] == i[notes[2]][info_part] == expected


@pytest.mark.parametrize(
    'notes', [
        (SpecificNote('C', 0), SpecificNote('C', 1)),
        (SpecificNote('d', 0), SpecificNote('d', 1)),
    ],
)
@pytest.mark.parametrize(
    'element, class_, info_part, keyarg, payload, expected', [
        ('rect', 'note', 'fill', 'note_colors', config.RED, config.RED),
        ('rect', 'top_rect', 'fill', 'top_rect_colors', config.RED, config.RED),
        ('rect', 'square', 'fill', 'squares', {'fill_color': config.RED}, config.RED),
        ('rect', 'square', 'stroke', 'squares', {'border_color': config.RED}, config.RED),
        ('text', 'square', 'fill', 'squares', {'text': 'T', 'text_color': config.RED}, config.RED),
        ('text', 'square', 'text', 'squares', {'text': 'T'}, 'T'),
        ('g', 'square', 'onclick', 'squares', {'onclick': 'T'}, 'T'),
    ],
)
@pytest.mark.parametrize('black_small', [True, False])
def test_specific(element, class_, info_part, keyarg, payload, expected, notes, black_small):
    svg = Piano(**{keyarg: {notes[0]: payload}}, black_small=black_small)._repr_svg_()  # type: ignore
    i = note_info(svg, element, class_)
    assert i[notes[0]][info_part] == expected

    if class_ == 'note' and info_part == 'fill':
        assert i[notes[1]][info_part] == note_color(notes[1])
    else:
        assert notes[1] not in i


@pytest.mark.parametrize(
    'notes', [
        (Note('C'), SpecificNote('C', 0), SpecificNote('C', 1)),
        (Note('d'), SpecificNote('d', 0), SpecificNote('d', 1)),
    ],
)
@pytest.mark.parametrize(
    'element, class_, info_part, keyarg, payload, expected', [
        ('rect', 'note', 'fill', 'note_colors', (config.RED, config.GREEN), (config.RED, config.GREEN)),
        ('rect', 'top_rect', 'fill', 'top_rect_colors', (config.RED, config.GREEN), (config.RED, config.GREEN)),
        ('rect', 'square', 'fill', 'squares', ({'fill_color': config.RED}, {'fill_color': config.GREEN}), (config.RED, config.GREEN)),
        ('rect', 'square', 'stroke', 'squares', ({'border_color': config.RED}, {'border_color': config.GREEN}), (config.RED, config.GREEN)),
        ('text', 'square', 'fill', 'squares', ({'text': 'T', 'text_color': config.RED}, {'text': 'T', 'text_color': config.GREEN}), (config.RED, config.GREEN)),
        ('text', 'square', 'text', 'squares', ({'text': 'T'}, {'text': 'Q'}), ('T', 'Q')),
        ('g', 'square', 'onclick', 'squares', ({'onclick': 'T'}, {'onclick': 'Q'}), ('T', 'Q')),
    ],
)
@pytest.mark.parametrize('black_small', [True, False])
def test_specific_overrides_abstract(element, class_, info_part, keyarg, payload, expected, notes, black_small):
    svg = Piano(**{keyarg: {notes[0]: payload[0], notes[2]: payload[1]}}, black_small=black_small)._repr_svg_()  # type: ignore
    i = note_info(svg, element, class_)
    assert i[notes[1]][info_part] == expected[0]
    assert i[notes[2]][info_part] == expected[1]


@pytest.mark.parametrize(
    'noterange, black_small, start, stop', [
        (NoteRange('d2', 'b2'), True, SpecificNote('C', 2), SpecificNote('B', 2)),
        (NoteRange('d2', 'b2'), False, SpecificNote('d', 2), SpecificNote('b', 2)),
    ],
)
def test_startswith_endswith_white_key(noterange, black_small, start, stop):
    svg = Piano(noterange=noterange, black_small=black_small)._repr_svg_()
    notes = note_info(svg, element='rect', class_='note').keys()
    assert min(notes) == start
    assert max(notes) == stop


def test_href_only_when_title():
    with pytest.raises(ValueError):
        Piano(title_href='T')
    with pytest.raises(ValueError):
        Piano(subtitle_href='T')
