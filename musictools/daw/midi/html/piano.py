def midi_piano_html():
    width, height = 1600, 5000

    svg = f'''
    <svg width='{width}px' height='{height}px'>
    </svg>
    '''

    html = f'''
    {svg}
    '''

    css = '''
    <style>
    svg {
        background-color: rgba(0,0,0, 0.04);
    }
    </style>
    '''
    html += css
    return html
    # with open('logs/vespers-04/main.html', 'w') as f: f.write(html)
