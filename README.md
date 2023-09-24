![GitHub tag (latest by date)](https://img.shields.io/github/v/tag/tandav/musiclib)

# musiclib
set of tools to work with scales, modes, modulations, chord progressions, voice leading, rhythm and more

## install
### install from [pypi](https://pypi.org/project/musiclib/)
```sh
pip install musiclib
```

### or install the latest version from github
```sh
pip install git+https://github.com/tandav/musiclib
```

### development
```sh
pip install -e .[dev]
```

## examples

```py
>>> from musiclib.scale import Scale
>>> from musiclib.noteset import SpecificNoteSet
>>> from musiclib.noterange import NoteRange

>>> scale = Scale.from_name('C', 'major')

>>> scale.root
Note('C')

>>> scale.notes
frozenset({Note('C'),
           Note('D'),
           Note('E'),
           Note('F'),
           Note('G'),
           Note('A'),
           Note('B')})

>>> scale.bits
'101011010101'

>>> scale.intervals
frozenset({0, 2, 4, 5, 7, 9, 11})
```

```py
Scale.from_name('C', 'phrygian')
```
![](docs/svg_examples/C_phrygian.svg)

```py
SpecificNoteSet.from_str('C1_e1_G1_C2_b2_E3')
```
![](docs/svg_examples/C1_e1_G1_C2_b2_E3.svg)

```py
NoteRange(SpecificNote('C', 1), SpecificNote('B', 3))
```
![](docs/svg_examples/noterange_C1_B3.svg)
