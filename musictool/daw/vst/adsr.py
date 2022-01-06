class ADSR:
    def __init__(
        self,
        attack: float = 0.,
        decay: float = 1e-3,
        sustain: float = 1.,
        release: float = 1e-3,
    ):
        # ranges like in Ableton Live Operator, Wavetable
        if not (0. <= attack <= 20.): raise ValueError('wrong attack value')
        if not (1e-3 <= decay <= 20.): raise ValueError('wrong decay value')
        if not (0. <= sustain <= 1.): raise ValueError('wrong sustain value')
        if not (1e-3 <= release <= 20.): raise ValueError('wrong release value')

        self.attack = attack
        self.decay = decay
        self.sustain = sustain
        self.release = release
