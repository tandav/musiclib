from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse

from scale import name_2_bits, all_scales, neighbors
import config

chromatic_notes_set = set(config.chromatic_notes)


app = FastAPI()

css = f'''
<style>
{open('main.css').read()}
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
    <a href='/'>home</a> | root: {roots}
    <h1>{root} scales</h1>
    <ol>
    {scales}
    </ol>
    {css}
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
    <a href='/'>home</a> | root: {roots} | scale: {scales}
    {s}
    <hr>
    {neighs_html}
    {css}
    '''
