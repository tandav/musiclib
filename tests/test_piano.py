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
    element: rect | text
    info_part be style_fill | style_stroke | text
    """
    out = collections.defaultdict(dict)
    for r in ElementTree.fromstring(svg).findall(f".//{element}/[@class='{class_}'][@note]"):
        note = SpecificNote.from_str(r.attrib['note'])
        if match := re.match('.*fill:#(.{6})', r.attrib['style']):
            out[note]['style_fill'] = int(match.group(1), base=16)
        if match := re.match('.*stroke:#(.{6})', r.attrib['style']):
            out[note]['style_stroke'] = int(match.group(1), base=16)
        if match := re.match('.*fill:#(.{6})', r.attrib['style']): # todo : fix pattern
            out[note]['text'] = int(match.group(1), base=16)
    return dict(out)


def colorize(element, class_, style_part, note_colors) -> dict[str, Any]:
    if element == 'rect':
        if class_ == 'note':
            return {'note_colors': note_colors}
        elif class_ == 'top_rect':
            return {'top_rect_colors': note_colors}
        elif class_ == 'square':
            # return {'squares': }
            pass
        else:
            raise ValueError


@pytest.mark.parametrize('element, class_, info_part', [
    ('rect', 'note', 'style_fill'),
    ('rect', 'top_rect', 'style_fill'),
    # ('rect', 'square', 'style_fill'),
])
def test_abstract(element, class_, info_part):
    svg = Piano(
        **colorize(element, class_, info_part, {Note('C'): config.RED}),
        # **{class_to_argname(element, class_, style_part): {Note('C'): config.RED}},
        noterange=NoteRange('C2', 'C3'),
    )._repr_svg_()
    i = note_info(svg, element, class_)
    assert i[SpecificNote('C', 2)][info_part] == i[SpecificNote('C', 3)][info_part] == config.RED


@pytest.mark.parametrize('element, class_, info_part', [
    ('rect', 'note', 'style_fill'),
    ('rect', 'top_rect', 'style_fill'),
])
def test_specific(element, class_, info_part):
    svg = Piano(
        **colorize(element, class_, info_part, {SpecificNote('C', 2): config.RED}),
        # **{class_to_argname(element, class_, style_part): {SpecificNote('C', 2): config.RED}},
        noterange=NoteRange('C2', 'C3'),
    )._repr_svg_()
    i = note_info(svg, element, class_)
    assert i[SpecificNote('C', 2)][info_part] == config.RED

    if class_ == 'note' and info_part == 'style_fill':
        assert i[SpecificNote('C', 3)][info_part] == config.WHITE_PALE
    else:
        assert SpecificNote('C', 3) not in i


@pytest.mark.parametrize('element, class_, info_part', [
    ('rect', 'note', 'style_fill'),
    ('rect', 'top_rect', 'style_fill'),
])
def test_specific_overrides_abstract(element, class_, info_part):
    svg = Piano(
        **colorize(element, class_, info_part, {Note('C'): config.RED, SpecificNote('C', 3): config.GREEN}),
        # **{class_to_argname(element, class_, style_part): {Note('C'): config.RED, SpecificNote('C', 3): config.GREEN}},
        noterange=NoteRange('C2', 'C3'),
    )._repr_svg_()
    i = note_info(svg, element, class_)
    assert i[SpecificNote('C', 2)][info_part] == config.RED
    assert i[SpecificNote('C', 3)][info_part] == config.GREEN


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
