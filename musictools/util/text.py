def cprint(*args, color=None, **kwargs):
    colormap = dict(
        BLACK='30m',
        RED='31m',
        GREEN='32m',
        YELLOW='33m',
        BLUE='34m',
        MAGENTA='35m',
        CYAN='36m',
        WHITE='37m',
        UNDERLINE='4m',
    )
    if color is None:
        print(*args, **kwargs)
    else:
        print('\033[' + colormap[color], end='')
        print(*args, **kwargs)
        print('\033[0m', end='')


def ago(e):
    # e: pass timedelta between timestamps in 1579812524 format
    e *= 1000  # convert to 1579812524000 format
    t = round(e / 1000)
    n = round(t / 60)
    r = round(n / 60)
    o = round(r / 24)
    i = round(o / 30)
    a = round(i / 12)
    if e < 0: return 'just now'
    elif t < 10: return 'just now'
    elif t < 45: return str(t) + ' seconds ago'
    elif t < 90: return 'a minute ago'
    elif n < 45: return str(n) + ' minutes ago'
    elif n < 90: return 'an hour ago'
    elif r < 24: return str(r) + ' hours ago'
    elif r < 36: return 'a day ago'
    elif o < 30: return str(o) + ' days ago'
    elif o < 45: return 'a month ago'
    elif i < 12: return str(i) + ' months ago'
    elif i < 18: return 'a year ago'
    else: return str(a) + ' years ago'
