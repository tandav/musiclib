from collections.abc import Sequence

import pytest

from musictool import config
from musictool.chord import Chord
from musictool.note import SpecificNote
from musictool.noterange import NoteRange
from musictool.noteset import NoteSet
from musictool.scale import Scale


@pytest.mark.parametrize(
    'start, stop, noteset, expected', (
        ('C0', 'C1', NoteSet(frozenset(config.chromatic_notes)), 'C0 d0 D0 e0 E0 F0 f0 G0 a0 A0 b0 B0 C1'),
        ('b3', 'E4', NoteSet(frozenset(config.chromatic_notes)), 'b3 B3 C4 d4 D4 e4 E4'),
        ('C0', 'C0', NoteSet(frozenset(config.chromatic_notes)), 'C0'),
        ('C0', 'C1', NoteSet(frozenset('CDEFGAB')), 'C0 D0 E0 F0 G0 A0 B0 C1'),
        ('C0', 'C1', Scale(frozenset('CDEFGAB'), root='C'), 'C0 D0 E0 F0 G0 A0 B0 C1'),
        ('C0', 'C1', Chord(frozenset('CDEFGAB'), root='C'), 'C0 D0 E0 F0 G0 A0 B0 C1'),
        ('a3', 'f4', NoteSet(frozenset('dEfaB')), 'a3 B3 d4 E4 f4'),
        ('A0', 'D2', NoteSet(frozenset('CDEFGAB')), 'A0 B0 C1 D1 E1 F1 G1 A1 B1 C2 D2'),
    ),
)
def test_note_range(start, stop, noteset, expected):
    assert list(NoteRange(SpecificNote.from_str(start), SpecificNote.from_str(stop), noteset)) == expected.split()


@pytest.mark.parametrize(
    'start, stop, noterange', (
        ('C0', 'C1', NoteRange(SpecificNote('C', 0), SpecificNote('C', 1))),
        ('E1', 'f3', NoteRange(SpecificNote('E', 1), SpecificNote('f', 3))),
        (SpecificNote('E', 1), 'f3', NoteRange(SpecificNote('E', 1), SpecificNote('f', 3))),
        ('E1', SpecificNote('f', 3), NoteRange(SpecificNote('E', 1), SpecificNote('f', 3))),
        (SpecificNote('E', 1), SpecificNote('f', 3), NoteRange(SpecificNote('E', 1), SpecificNote('f', 3))),
    ),
)
def test_note_range_from_str(start, stop, noterange):
    assert NoteRange(start, stop) == noterange


def test_noterange_bounds():
    with pytest.raises(ValueError): NoteRange(SpecificNote('D', 2), SpecificNote('C', 1))
    with pytest.raises(KeyError): NoteRange(SpecificNote('C', 1), SpecificNote('C', 2), noteset=NoteSet(frozenset()))
    with pytest.raises(KeyError): NoteRange(SpecificNote('C', 1), SpecificNote('D', 2), noteset=NoteSet(frozenset('Cd')))
    with pytest.raises(KeyError): NoteRange(SpecificNote('C', 1), SpecificNote('D', 2), noteset=NoteSet(frozenset('dD')))
    with pytest.raises(KeyError): NoteRange(SpecificNote('C', 1), SpecificNote('D', 2), noteset=NoteSet(frozenset('dDeE')))


def test_noterange_contains():
    assert SpecificNote('D', 1) in NoteRange(SpecificNote('C', 1), SpecificNote('C', 2))
    assert SpecificNote('C', 1) in NoteRange(SpecificNote('C', 1), SpecificNote('C', 2))
    assert SpecificNote('C', 2) in NoteRange(SpecificNote('C', 1), SpecificNote('C', 2))
    assert SpecificNote('C', 3) not in NoteRange(SpecificNote('C', 1), SpecificNote('C', 2))
    assert SpecificNote('D', 1) not in NoteRange(SpecificNote('C', 1), SpecificNote('F', 1), noteset=NoteSet(frozenset('CEF')))


@pytest.mark.parametrize(
    'start, stop, notes, length', (
        (SpecificNote('C', 1), SpecificNote('G', 1), 'CdDeEFfGaAbB', 8),
        (SpecificNote('D', 1), SpecificNote('G', 3), 'CdDeEFfGaAbB', 30),
        (SpecificNote('D', 1), SpecificNote('D', 1), 'CdDeEFfGaAbB', 1),
        (SpecificNote('E', 1), SpecificNote('b', 1), 'CDEFGAb', 5),
        (SpecificNote('b', 1), SpecificNote('G', 3), 'CDEFGAb', 13),
        (SpecificNote('f', 1), SpecificNote('a', 1), 'fa', 2),
        (SpecificNote('f', 1), SpecificNote('f', 2), 'fa', 3),
        (SpecificNote('f', 1), SpecificNote('a', 3), 'fa', 6),
        (SpecificNote('f', 1), SpecificNote('f', 3), 'f', 3),
    ),
)
def test_noterange_len(start, stop, notes, length):
    assert len(NoteRange(start, stop, NoteSet(frozenset(notes)))) == length


def test_noterange_getitem():
    nr = NoteRange(SpecificNote('C', 1), SpecificNote('C', 2))
    assert nr[0] == nr[-13] == SpecificNote('C', 1)
    assert nr[1] == nr[-12] == SpecificNote('d', 1)
    assert nr[2] == nr[-11] == SpecificNote('D', 1)
    assert nr[12] == nr[-1] == SpecificNote('C', 2)
    assert nr[11] == nr[-2] == SpecificNote('B', 1)
    assert nr[0:0] == NoteRange(SpecificNote('C', 1), SpecificNote('C', 1))
    assert nr[0:1] == NoteRange(SpecificNote('C', 1), SpecificNote('d', 1))
    assert nr[0:2] == NoteRange(SpecificNote('C', 1), SpecificNote('D', 1))
    assert nr[0:12] == NoteRange(SpecificNote('C', 1), SpecificNote('C', 2))
    assert nr[1:] == NoteRange('d1', 'C2')
    assert nr[:4] == NoteRange('C1', 'E1')
    assert nr[:] == NoteRange('C1', 'C2')

    with pytest.raises(IndexError): nr[13]
    with pytest.raises(IndexError): nr[-14]
    with pytest.raises(IndexError): nr[-3: 1]
    with pytest.raises(IndexError): nr[5: 13]

    ns = NoteSet(frozenset('fa'))
    nr = NoteRange(SpecificNote('f', -1), SpecificNote('a', 3), ns)
    assert nr[0] == nr[-10] == SpecificNote('f', -1)
    assert nr[1] == nr[-9] == SpecificNote('a', -1)
    assert nr[2] == nr[-8] == SpecificNote('f', 0)
    assert nr[9] == nr[-1] == SpecificNote('a', 3)
    assert nr[8] == nr[-2] == SpecificNote('f', 3)
    assert nr[0:0] == NoteRange(SpecificNote('f', -1), SpecificNote('f', -1), ns)
    assert nr[0:1] == NoteRange(SpecificNote('f', -1), SpecificNote('a', -1), ns)
    assert nr[0:2] == NoteRange(SpecificNote('f', -1), SpecificNote('f', 0), ns)
    assert nr[0:9] == NoteRange(SpecificNote('f', -1), SpecificNote('a', 3), ns)
    with pytest.raises(IndexError): nr[10]
    with pytest.raises(IndexError): nr[-11]


@pytest.mark.parametrize(
    'noterange, expected', [
        (NoteRange(SpecificNote('C', 1), SpecificNote('C', 2)), 'C1 d1 D1 e1 E1 F1 f1 G1 a1 A1 b1 B1 C2'),
        (NoteRange(SpecificNote('b', 1), SpecificNote('D', 2), noteset=NoteSet(frozenset('AbBCdDe'))), 'b1 B1 C2 d2 D2'),
    ],
)
def test_noterange_list(noterange, expected):
    assert list(noterange) == [SpecificNote.from_str(s) for s in expected.split()]


def test_sequence():
    nr = NoteRange(SpecificNote('C', 1), SpecificNote('C', 2))
    assert isinstance(nr, Sequence)


TITLE = 'title_fUYsZHfC'
SUBTITLE = 'subtitle_EfrKTj'
HEADER_HREF = 'header_href_TUMhv'


@pytest.mark.parametrize(
    'noterange', [
        NoteRange('C2', 'C5'),
        NoteRange('D2', 'G2', noteset=NoteSet.from_str('CDG')),
    ],
)
@pytest.mark.parametrize('title', (None, TITLE))
@pytest.mark.parametrize('subtitle', (None, SUBTITLE))
@pytest.mark.parametrize('header_href', (None, HEADER_HREF))
def test_html(noterange, title, subtitle, header_href):
    html_classes = ('cls1', 'cls2')
    html = noterange._repr_html_(
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
