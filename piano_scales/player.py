from collections.abc import Iterable
from numbers import Number
import time
import mido
from . import config
from .note import Note

def play(notes: Iterable[Note], seconds: Number):
    for note in notes: config.port.send(mido.Message('note_on', note=note))
    time.sleep(seconds)
    for note in notes: config.port.send(mido.Message('note_off', note=note))