import asyncio
import mido

from piano_scales import config
from piano_scales.scale import all_scales
# device = 'IAC Driver Bus 1'
# port = mido.open_output(device)

# async def play_note(note, seconds=1):
#     print('note_on', note, seconds, 'seconds')
#     config.port.send(mido.Message('note_on', note=note))
#     await asyncio.sleep(seconds)
#     print('note_off', note)
#     config.port.send(mido.Message('note_off', note=note))

async def main():
    s = all_scales['diatonic']['D', 'dorian']

    for chord in s.chords:
        await chord.play()
        # tasks = (note.play() for note in chord.notes)
        # await asyncio.gather(*tasks)

    #     print(chord.str_chord, chord.root_octave)
    #     await chord.play(seconds=1)

    print('Hello ...')
    # await asyncio.gather(
    #     play_note(60),
    #     play_note(64),
    #     play_note(67),
    # )
    # await asyncio.sleep(1)
    print('... World!')

# Python 3.7+
asyncio.run(main())