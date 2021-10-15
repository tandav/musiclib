import pytest

from musictools.daw import render
from musictools.daw import vst as vst_

vst0 = vst_.Sine(adsr=vst_.ADSR(attack=0.05, decay=0.3, sustain=0.1, release=0.001))
vst1 = vst_.Sine(adsr=vst_.ADSR(attack=0.001, decay=0.3, sustain=1, release=2))
vst2 = vst_.Organ(adsr=vst_.ADSR(attack=0.001, decay=0.15, sustain=0, release=0.1))
vst3 = vst_.Sampler(adsr=vst_.ADSR(attack=0.001, decay=0.15, sustain=0, release=0.1))


@pytest.fixture(params=[vst0, vst1, vst2, vst3])
def vst(request):
    yield request.param


@pytest.fixture(params=[render.single, render.chunked])
def renderer(request):
    yield request.param
