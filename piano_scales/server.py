from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from . import config
from .chord import SpecificChord
from .note import SpecificNote
from .scale import ComparedScale
from .scale import all_scales
from .scale import majors

chromatic_notes_set = set(config.chromatic_notes)

static_folder = Path(__file__).parent / 'static'

app = FastAPI()
app.mount("/static/", StaticFiles(directory=static_folder), name="static")


@app.get("/scale_not_found", response_class=HTMLResponse)
def scale_not_found():
    return '''
    <header><a href='/'>home</a></header>
    <h1>404: scale not found</h1>
    '''


@app.get("/play_chord/{chord}")
async def play_chord(chord: str):
    print('PLAYIN CHORD', chord)
    notes = tuple(SpecificNote(n, octave=5) for n in chord)
    raise NotImplementedError('REWRITE: instead of rely on 1st note explicitly pass root CEG_C')
    await SpecificChord(frozenset(notes), root=notes[0]).play(bass=-1)
    return {'status': 'play_chord success'}


@app.get("/play_note/{note}/{octave}")
async def play_note(note: str, octave: int):
    print('PLAYIN NOTE', note, octave)
    await SpecificNote(note, octave).play()
    return {'status': 'play_note success'}


@app.get("/", response_class=HTMLResponse)
async def root(): return RedirectResponse('/diatonic/C/major')


@app.get("/favicon.ico", response_class=HTMLResponse)
async def favicon(): return FileResponse(static_folder / 'favicon.ico')


@app.get("/circle", response_class=HTMLResponse)
async def circle():

    html = '''\
    <link rel="stylesheet" href="static/circle.css">
    <link rel="stylesheet" href="/static/main.css">
    <script src="/static/play.js"></script>
    '''

    tmp = ''

    for i, scale in enumerate(majors, start=1):
        # html += f"<div class='circle _{i}'>{i}</div>"
        # html += scale.with_html_classes(('kinda_circle', f'_{i}'))
        tmp += scale.with_html_classes(('kinda_circle', f'_{i}'))

    return html + f"<div class='container'>{tmp}</div>"


@app.get("/circle/{selected_major}", response_class=HTMLResponse)
async def circle_selected(selected_major: str):

    html = '''\
    <link rel="stylesheet" href="/static/circle.css">
    <link rel="stylesheet" href="/static/main.css">
    <script src="/static/play.js"></script>
    '''

    selected = all_scales['diatonic'][selected_major, 'major']

    for i, scale in enumerate(majors, start=1):
        if scale == selected:
            html += ComparedScale(selected, scale).with_html_classes(('kinda_circle', f'_{i}', 'selected_scale'))
        else:
            html += ComparedScale(selected, scale).with_html_classes(('kinda_circle', f'_{i}'))
    return html


# @app.get("/{kind}", response_class=HTMLResponse)
# async def kind(kind: str):
#     return RedirectResponse(f'/{kind}/C/{getattr(config, kind)[0]}')
#
# @app.get("/{kind}/{root}", response_class=HTMLResponse)
# async def kind_root(kind: str, root: str): return RedirectResponse(f'/{kind}/{root}/{getattr(config, kind)[0]}')
#
#
# @app.get("/{kind}/{root}/{name}", response_class=HTMLResponse)
# async def root_name_scale(kind: str, root: str, name: str, load_all=False):
#
#     if root not in chromatic_notes_set:
#         return RedirectResponse('/scale_not_found')
#
#     roots = ' '.join(f"<a href='/{kind}/{note}/{name}'>{note}</a>" for note in config.chromatic_notes)
#
#     initial = []
#     for _name in util.iter_scales(kind):
#         scale = all_scales[kind][root, _name]
#         if _name == name:
#             initial.append(scale.with_html_classes(('selected_scale',)))
#             selected_scale = scale
#         else:
#             initial.append(scale._repr_html_())
#     initial = '\n'.join(initial)
#
#     neighs = neighbors(selected_scale)
#     neighs_html = ''
#
#     if load_all:
#         min_shared = 0
#     else:
#         min_shared = config.neighsbors_min_shared[kind]
#
#     for n_intersect in sorted(neighs.keys(), reverse=True):
#         if n_intersect < min_shared:
#             break
#         neighs_html += f'''
#         <h3>{n_intersect} shared notes{f', {util.n_intersect_notes_to_n_shared_chords[n_intersect]} shared chords (click to see)' if kind == 'diatonic' else ''}</h3>
#         <div class="neighbors">
#         {''.join(n._repr_html_() for n in neighs[n_intersect])}
#         </div>
#         <hr>
#         '''
#
#     kind_links = f"<a href='/diatonic/{root}/major'>diatonic</a>"
#     kind_links += f" <a href='/pentatonic/{root}/p_major'>pentatonic</a>"
#
#     return f'''
#     <link rel="stylesheet" href="/static/main.css">
#     <header><a href='/'>home</a> <a href='https://github.com/tandav/piano_scales'>github</a> | root: {roots} | {kind_links} | <a href='/circle'>circle</a></header>
#     <hr>
#     <h3>select scale</h3>
#     <div class='initial'>{initial}</div>
#     <hr>
#     {neighs_html}
#     {'' if min_shared == 0 else f"<a href='/{kind}/{root}/{name}/all'>load all scales</a>"}
#     '''
#
# @app.get("/{kind}/{root}/{name}/all", response_class=HTMLResponse)
# async def root_name_scale_load_all(kind: str, root: str, name: str):
#     return await root_name_scale(kind, root, name, load_all=True)
#
#
# @app.get("/{kind}/{left_root}/{left_name}/compare_to/{right_root}/{right_name}/", response_class=HTMLResponse)
# async def compare_scales(kind: str, left_root: str, left_name: str, right_root: str, right_name: str):
#     roots = ' '.join(f"<a href='/{kind}/{note}/{left_name}'>{note}</a>" for note in config.chromatic_notes)
#     kind_links = f"<a href='/diatonic/{left_root}/major'>diatonic</a>"
#     kind_links += f" <a href='/pentatonic/{left_root}/p_major'>pentatonic</a>"
#
#     left = all_scales[kind][left_root, left_name]
#     right = ComparedScale(left, all_scales[kind][right_root, right_name])
#     n_shared_notes  = len(right.shared_notes)
#     n_shared_chords = len(right.shared_chords)
#
#     for i, chord in enumerate(left.chords, start=1):
#         chord.number = i
#         if chord in right.shared_chords:
#             chord.label = f'left_{chord.str_chord}'
#
#     for i, chord in enumerate(right.chords, start=1):
#         chord.number = i
#         if chord in right.shared_chords:
#             chord.label = f'right_{chord.str_chord}'
#
#     js = '''
#     const arrows = []
#     '''
#
#     for chord in right.shared_chords:
#         #js += f"new LeaderLine(document.getElementById('left_{chord.str_chord}'), document.getElementById('right_{chord.str_chord}')).setOptions({{startSocket: 'bottom', endSocket: 'top'}});\n"
#         js += f'''
#         arrows.push(new LeaderLine(document.getElementById('left_{chord.str_chord}'), document.getElementById('right_{chord.str_chord}')))
#         '''
#
#     js += '''
#     const updateArrows = () => {
#         if (window.innerWidth <= 1080) {
#             var startSocket = 'right'
#             var endSocket = 'left'
#         } else {
#             var startSocket = 'bottom'
#             var endSocket = 'top'
#         }
#
#         for (const arrow of arrows) {
#             arrow.setOptions({startSocket: startSocket, endSocket: endSocket})
#         }
#     }
#     updateArrows()
#     window.onresize = updateArrows
#     '''
#
#     return f'''
#     <link rel="stylesheet" href="/static/main.css">
#     <script src="/static/leader-line.min.js"></script>
#     <script src="/static/play.js"></script>
#
#     <header><a href='/'>home</a> <a href='https://github.com/tandav/piano_scales'>github</a> | root: {roots} | {kind_links}</header>
#     <h1>compare scales</h1>
#     <p>{n_shared_notes} shared notes, {n_shared_chords} shared chords</p>
#     <div class='compare_scales'>
#     <div class='left'>{left!r}</div>
#     <div class='right'>{right!r}</div></div>
#     <h1>chords</h1>
#     <div class='compare_chords'>
#     <ol class='chords_row left'>{''.join(f'{chord!r}' for chord in left.chords)}</ol>
#     <ol class='chords_row right'>{''.join(f'{chord!r}' for chord in right.chords)}</ol>
#     <script>
#     {js}
#     </script>
#     </div>
#     '''

# @app.get("/{kind}/{left_root}/{left_name}/compare_to/{right_root}/{right_name}/play_chord_{chord}", response_class=HTMLResponse)
# async def play_chord(kind: str, left_root: str, left_name: str, right_root: str, right_name: str, chord: str):
#     print('PLAYIN CHORD', chord)
#     await Chord(chord).play(bass=-2)
#     return await compare_scales(kind, left_root, left_name, right_root, right_name)

# @app.get("/{kind}/{root}/{name}/all_chords", response_class=HTMLResponse)
# async def all_chords(kind: str, root: str, name: str):
#
#     if root not in chromatic_notes_set:
#         return RedirectResponse('/scale_not_found')
#
#     roots = ' '.join(f"<a href='/{kind}/{note}/{name}/all_chords'>{note}</a>" for note in config.chromatic_notes)
#     kind_links = f"<a href='/diatonic/{root}/major'>diatonic</a>"
#     kind_links += f" <a href='/pentatonic/{root}/p_major'>pentatonic</a>"
#
#
#     scale = all_scales[kind][root, name]
#     n = scale
#     payload = f"<div class='chord_buttons_row'><span class='scale_name {n.name}'>{n.root} {n.name}</span>" + ''.join(f"<span class='chord_button {chord.name}' onclick=play_chord('{chord.str_chord}')>{i}</span>\n" for i, chord in enumerate(n.chords, start=1)) + '</div>\n'
#     neighs = neighbors(scale)
#     for n_intersect in sorted(neighs.keys(), reverse=True):
#         payload += f"<h3>{n_intersect} shared notes{f', {util.n_intersect_notes_to_n_shared_chords[n_intersect]} shared chords' if kind == 'diatonic' else ''}</h3>\n"
#         for n in neighs[n_intersect]:
#             payload += f"<div class='chord_buttons_row'><span class='scale_name {n.name}'>{n.root} {n.name}</span>"
#             for i, chord in enumerate(n.chords, start=1):
#                 is_shared = 'is_shared' if chord in n.shared_chords else ''
#                 payload += f"<span class='chord_button {chord.name} {is_shared}' onclick=play_chord('{chord.str_chord}')>{i}</span>\n"
#             payload += '</div>\n'
#
#     return f'''
#     <link rel="stylesheet" href="/static/main.css">
#     <script src="/static/play.js"></script>
#
#     <header><a href='/'>home</a> <a href='https://github.com/tandav/piano_scales'>github</a> | root: {roots} | {kind_links}</header>
#     <hr><br>
#     {payload}
#     '''
