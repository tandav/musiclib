import re
import collections
from xml.etree import ElementTree
from typing import Any

import pytest

from musictool import config
from musictool.note import Note
from musictool.note import SpecificNote
from musictool.noterange import NoteRange
from musictool.piano import Piano
from musictool.piano import note_color


@pytest.mark.parametrize('note, color', [
    (Note('C'), config.WHITE_PALE),
    (Note('d'), config.BLACK_PALE),
    (SpecificNote('C', 1), config.WHITE_PALE),
    (SpecificNote('d', 1), config.BLACK_PALE),
])
def test_note_color(note, color):
    assert note_color(note) == color


def note_info(svg: str, element: str, class_: str) -> dict[SpecificNote, dict[str, str | int]]:
    """
    element: rect | text | g
    info_part be style_fill | style_stroke | text | text_color | onclick
    """
    out = collections.defaultdict(dict)
    for r in ElementTree.fromstring(svg).findall(f".//{element}/[@class='{class_}'][@note]"):
        note = SpecificNote.from_str(r.attrib['note'])
        if style := r.attrib.get('style'):
            if match := re.match('.*fill:#(.{6})', style):
                out[note]['style_fill'] = int(match.group(1), base=16)
            if match := re.match('.*stroke:#(.{6})', style):
                out[note]['style_stroke'] = int(match.group(1), base=16)
        if text := r.text:
            out[note]['text'] = text
        if onclick := r.attrib.get('onclick'):
            out[note]['onclick'] = onclick
    return dict(out)


@pytest.mark.parametrize('element, class_, info_part, keyarg, payload, expected', [
    ('rect', 'note', 'style_fill', 'note_colors', config.RED, config.RED),
    ('rect', 'top_rect', 'style_fill', 'top_rect_colors', config.RED, config.RED),
    ('rect', 'square', 'style_fill', 'squares', {'fill_color': config.RED}, config.RED),
    ('rect', 'square', 'style_stroke', 'squares', {'border_color': config.RED}, config.RED),
    ('text', 'square', 'style_fill', 'squares', {'text': 'T', 'text_color': config.RED}, config.RED),
    ('text', 'square', 'text', 'squares', {'text': 'T'}, 'T'),
    ('g', 'square', 'onclick', 'squares', {'onclick': 'T'}, 'T'),
])
def test_abstract(element, class_, info_part, keyarg, payload, expected):
    svg = Piano(**{keyarg: {Note('C'): payload}}, noterange=NoteRange('C2', 'C3'))._repr_svg_()
    i = note_info(svg, element, class_)
    assert i[SpecificNote('C', 2)][info_part] == i[SpecificNote('C', 3)][info_part] == expected


@pytest.mark.parametrize('element, class_, info_part, keyarg, payload, expected', [
    ('rect', 'note', 'style_fill', 'note_colors', config.RED, config.RED),
    ('rect', 'top_rect', 'style_fill', 'top_rect_colors', config.RED, config.RED),
    ('rect', 'square', 'style_fill', 'squares', {'fill_color': config.RED}, config.RED),
    ('rect', 'square', 'style_stroke', 'squares', {'border_color': config.RED}, config.RED),
    ('text', 'square', 'style_fill', 'squares', {'text': 'T', 'text_color': config.RED}, config.RED),
    ('text', 'square', 'text', 'squares', {'text': 'T'}, 'T'),
    ('g', 'square', 'onclick', 'squares', {'onclick': 'T'}, 'T'),
])
def test_specific(element, class_, info_part, keyarg, payload, expected):
    svg = Piano(**{keyarg: {SpecificNote('C', 2): payload}}, noterange=NoteRange('C2', 'C3'))._repr_svg_()
    i = note_info(svg, element, class_)
    assert i[SpecificNote('C', 2)][info_part] == expected

    if class_ == 'note' and info_part == 'style_fill':
        assert i[SpecificNote('C', 3)][info_part] == config.WHITE_PALE
    else:
        assert SpecificNote('C', 3) not in i


@pytest.mark.parametrize('element, class_, info_part, keyarg, payload, expected', [
    ('rect', 'note', 'style_fill', 'note_colors', (config.RED, config.GREEN), (config.RED, config.GREEN)),
    ('rect', 'top_rect', 'style_fill', 'top_rect_colors', (config.RED, config.GREEN), (config.RED, config.GREEN)),
    ('rect', 'square', 'style_fill', 'squares', ({'fill_color': config.RED}, {'fill_color': config.GREEN}), (config.RED, config.GREEN)),
    ('rect', 'square', 'style_stroke', 'squares', ({'border_color': config.RED}, {'border_color': config.GREEN}), (config.RED, config.GREEN)),
    ('text', 'square', 'style_fill', 'squares', ({'text': 'T', 'text_color': config.RED}, {'text': 'T', 'text_color': config.GREEN}), (config.RED, config.GREEN)),
    ('text', 'square', 'text', 'squares', ({'text': 'T'}, {'text': 'Q'}), ('T', 'Q')),
    ('g', 'square', 'onclick', 'squares', ({'onclick': 'T'}, {'onclick': 'Q'}), ('T', 'Q')),
])
def test_specific_overrides_abstract(element, class_, info_part, keyarg, payload, expected):
    svg = Piano(
        **{keyarg: {Note('C'): payload[0], SpecificNote('C', 3): payload[1]}},
        noterange=NoteRange('C2', 'C3'),
    )._repr_svg_()
    i = note_info(svg, element, class_)
    assert i[SpecificNote('C', 2)][info_part] == expected[0]
    assert i[SpecificNote('C', 3)][info_part] == expected[1]


def test_startswith_endswith_white_key():
    svg = Piano(noterange=NoteRange('d2', 'b2'))._repr_svg_()
    notes = note_info(svg, element='rect', class_='note').keys()
    assert min(notes) == SpecificNote('C', 2)
    assert max(notes) == SpecificNote('B', 2)


# @pytest.mark.parametrize('payload', [
#     {'text': 'T'},
# ])
# def test_square_partial_payload(payload):
#     svg = Piano(
#         squares={Note('C'): payload},
#         noterange = NoteRange('C2', 'C3'),
#     )
#     i =
#     assert text('C1') == text('C2') == 'T'
