from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse

from scale import name_2_bits
import config

app = FastAPI()

roots = ' '.join(f"<a href='/scale/{note}'>{note}</a>" for note in config.chromatic_notes)


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
    scales = '\n'.join(f"<li><a href='/scale/{root}/{name}'>{root} {name}</a></li>" for name in name_2_bits)
    return f'''
    <a href='/'>home</a><br>
    root: {roots}
    <h1>{root} scales</h1>
    <ol>
    {scales}
    </ol>
    '''


@app.get("/scale/{root}/{name}", response_class=HTMLResponse)
async def root_name_scale(root: str, name: str):

    if root not in config.chromatic_notes:
        return RedirectResponse('/scale_not_found')

    return f'''
    <a href='/'>home</a>
    <h1>{root} {name}</h1>
    <code>bits: {name_2_bits[name]}</code>
    '''



# @app.get("/cleanup", response_class=HTMLResponse)
# async def root():
#     util.clean_input()
#     lines[:] = config.INPUT.read_text().splitlines()
#     return RedirectResponse(f'/item/0')
#
#
# @app.get("/item/{item_id}", response_class=HTMLResponse)
# async def item_info(item_id: int):
#     title, url = util.parse_markdown_link(lines[item_id])
#
#     target_links = '\n'.join(
#         f"<code>>> <a href='/item/{item_id}/move_to_target/{target_id}'>{target}</a></code><br>"
#         for target_id, target in enumerate(targets)
#     )
#
#     percentage = round(item_id / len(lines) * 100, 4)
#
#     return f'''
#     <pre><a href='/'>home</a> <a href='/cleanup'>cleanup</a></pre>
#     <pre>{config.INPUT}</pre>
#     <code>- [<a href='{url}' target='_blank'>{title}</a>]({url})</code>
#     <br><br>
#     <pre>{f'{item_id} / {len(lines)} {percentage}%'}</pre>
#     {util.button('prev', f'/item/{item_id - 1}')}
#     {util.button('next', f'/item/{item_id + 1}')}
#     <hr>
#     {target_links}
#     '''
#
#
# @app.get("/item/{item_id}/move_to_target/{target_id}")
# async def move_item_to_target(item_id: int, target_id: int):
#     line = lines[item_id]
#     target = targets[target_id]
#     print(line)
#     print('>>', target)
#     print('-' * 64)
#     with open(config.root / target, 'a') as f:
#         print(line, file=f)
#     return RedirectResponse(f'/item/{item_id + 1}')
