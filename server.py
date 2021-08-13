from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from scale import name_2_bits, all_scales, neighbors, ComparedScale
import config

chromatic_notes_set = set(config.chromatic_notes)


app = FastAPI()
app.mount("/static/", StaticFiles(directory="static"), name="static")

css = f'''
<style>
{open('static/main.css').read()}
</style>
'''

@app.get("/scale_not_found", response_class=HTMLResponse)
def scale_not_found():
    return f'''
    <a href='/'>home</a>
    <h1>404: scale not found</h1>
    '''

@app.get("/", response_class=HTMLResponse)
async def root():
    return RedirectResponse('/scale/C')


@app.get("/scale/{root}", response_class=HTMLResponse)
async def root_scales(root: str):
    roots = ' '.join(f"<a href='/scale/{note}'>{note}</a>" for note in config.chromatic_notes)
    scales = '\n'.join(f"<li><a href='/scale/{root}/{name}'>{root} {name}</a></li>" for name in name_2_bits)

    return f'''
    <link rel="stylesheet" href="/static/main.css">
    <a href='/'>home</a> <a href='https://github.com/tandav/piano_scales'>github</a> | root: {roots}
    <h1>{root} scales</h1>
    <ol>
    {scales}
    </ol>
    '''


@app.get("/scale/{root}/{name}", response_class=HTMLResponse)
async def root_name_scale(root: str, name: str):

    if root not in chromatic_notes_set:
        return RedirectResponse('/scale_not_found')

    roots = ' '.join(f"<a href='/scale/{note}/{name}'>{note}</a>" for note in config.chromatic_notes)
    scales = ' '.join(f"<a href='/scale/{root}/{name}'>{name}</a>" for name in name_2_bits)

    s = all_scales[root, name]
    neighs = neighbors(s)
    neighs_html = ''

    for n_intersect in sorted(neighs.keys(), reverse=True):
        print(n_intersect)
        if n_intersect < config.neighsbors_min_intersect:
            break
        neighs_html += f'''
        <h3>{n_intersect} note intersection scales</h3>
        <div class="neighbors">
        {''.join(repr(n) for n in neighs[n_intersect])}
        </div>
        <hr>
        '''

    return f'''
    <link rel="stylesheet" href="/static/main.css">
    <a href='/'>home</a> <a href='https://github.com/tandav/piano_scales'>github</a> | root: {roots} | scale: {scales}
    {s!r}
    <hr>
    {neighs_html}
    '''

@app.get("/scale/{left_root}/{left_name}/compare_to/{right_root}/{right_name}", response_class=HTMLResponse)
async def compare_scales(left_root: str, left_name: str, right_root: str, right_name: str):
    left = all_scales[left_root, left_name]
    right = ComparedScale(left, all_scales[right_root, right_name])


    for i, chord in enumerate(left.chords, start=1):
        if chord in right.shared_chords:
            chord.label = f'left_{chord.str_chord}'

    for i, chord in enumerate(right.chords, start=1):
        if chord in right.shared_chords:
            chord.label = f'right_{chord.str_chord}'

    js = '\n'
    for chord in right.shared_chords:
        js += f"new LeaderLine(document.getElementById('left_{chord.str_chord}'), document.getElementById('right_{chord.str_chord}'))\n"

    return f'''
    <link rel="stylesheet" href="/static/main.css">
    <script src="/static/leader-line.min.js"></script>
    
    <a href='/'>home</a> <a href='https://github.com/tandav/piano_scales'>github</a>
    <h1>compare scales</h1>
    <div class='compare_scales'>{left!r}{right!r}</div>
    <h1>chords</h1>
    <div class='compare_scales'>
    <ol class='left'>{''.join(f'{chord!r}' for chord in left.chords)}</ol>
    <ol class='right'>{''.join(f'{chord!r}' for chord in right.chords)}</ol>
    <script>
    {js}
    </script>
    </div>
    '''