from musiclib.svg.pianoroll import PianoRoll


def test_repr_svg(midi):
    PianoRoll(midi)._repr_svg_()
