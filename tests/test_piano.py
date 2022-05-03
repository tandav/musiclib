import re
from xml.etree import ElementTree

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


def note_colors(svg: str, element: str, class_: str, style_part: str = None) -> dict[SpecificNote, int]:
    """
    element: rect | text
    style_part be fill | stroke
    """
    out = {}
    for r in ElementTree.fromstring(svg).findall(f"{element}/[@class='{class_}'][@note]"):
        note = SpecificNote.from_str(r.attrib['note'])
        out[note] = int(re.match('.*' + style_part + ':#(.{6})', r.attrib['style']).group(1), base=16)
    return out


class_to_argname = {'note': 'note_colors', 'top_rect': 'top_rect_colors'}


@pytest.mark.parametrize('element, class_, style_part', [
    ('rect', 'note', 'fill'),
    ('rect', 'top_rect', 'fill'),
])
def test_abstract(element, class_, style_part):
    svg = Piano(**{class_to_argname[class_]: {Note('C'): config.RED}}, noterange=NoteRange('C2', 'C3'))._repr_svg_()
    nc = note_colors(svg, element, class_, style_part)
    assert nc[SpecificNote('C', 2)] == nc[SpecificNote('C', 3)] == config.RED


@pytest.mark.parametrize('element, class_, style_part', [
    ('rect', 'note', 'fill'),
    ('rect', 'top_rect', 'fill'),
])
def test_specific(element, class_, style_part):
    svg = Piano(**{class_to_argname[class_]: {SpecificNote('C', 2): config.RED}}, noterange=NoteRange('C2', 'C3'))._repr_svg_()
    nc = note_colors(svg, element, class_, style_part)
    assert nc[SpecificNote('C', 2)] == config.RED

    c3 = nc.get(SpecificNote('C', 3))
    assert c3 is None or c3 == config.WHITE_PALE


@pytest.mark.parametrize('element, class_, style_part', [
    ('rect', 'note', 'fill'),
    ('rect', 'top_rect', 'fill'),
])
def test_specific_overrides_abstract(element, class_, style_part):
    svg = Piano(
        **{class_to_argname[class_]: {Note('C'): config.RED, SpecificNote('C', 3): config.GREEN}},
        noterange=NoteRange('C2', 'C3'),
    )._repr_svg_()
    nc = note_colors(svg, element, class_, style_part)
    assert nc[SpecificNote('C', 2)] == config.RED
    assert nc[SpecificNote('C', 3)] == config.GREEN


def test_startswith_endswith_white_key():
    svg = Piano(noterange=NoteRange('d2', 'b2'))._repr_svg_()
    notes = note_colors(svg, element='rect', class_='note', style_part='fill').keys()
    assert min(notes) == SpecificNote('C', 2)
    assert max(notes) == SpecificNote('B', 2)
