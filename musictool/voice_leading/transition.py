from musictool.chord import SpecificChord
from musictool.note import SpecificNote


class Transition:
    def __init__(self, a: SpecificChord, b: SpecificChord):
        self.a = a
        self.b = b

    @staticmethod
    def arrow(a: SpecificNote, b: SpecificNote):
        if a < b: return '︎\\'
        elif a == b: return '|'
        else: return '/'

    def __repr__(self):
        return '\n'.join((
            str(self.a),
            '  '.join(self.arrow(na, nb) for na, nb in zip(self.a, self.b)),
            str(self.b),
        ))
