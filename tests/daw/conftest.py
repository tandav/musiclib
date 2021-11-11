import pytest

from musictools.daw.vst.adsr import ADSR
from musictools.daw.vst.organ import Organ
from musictools.daw.vst.sampler import Sampler
from musictools.daw.vst.sine import Sine
from musictools.daw.vst.sine import Sine8

vst0 = Sine(adsr=ADSR(attack=0.05, decay=0.3, sustain=0.1, release=0.001))
vst1 = Sine(adsr=ADSR(attack=0.001, decay=0.3, sustain=1, release=2))
vst2 = Organ(adsr=ADSR(attack=0.001, decay=0.15, sustain=0, release=0.1))
vst3 = Sampler()
vst4 = Sine8()


@pytest.fixture(params=[vst0, vst1, vst2, vst3])
def vst(request):
    yield request.param


@pytest.fixture
def single_vst():
    yield vst0


# @pytest.fixture(params=[render.single, render.chunked])
# def renderer(request):
#     yield request.param


# def stream():
#     yield Bytes()
