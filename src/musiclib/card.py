from __future__ import annotations

import abc
import typing

if typing.TYPE_CHECKING:
    from musiclib.noterange import NoteRange


class Card(abc.ABC):
    @staticmethod
    def repr_card(
        html_classes: tuple[str, ...] = (),
        title: str | None = None,
        subtitle: str | None = None,
        header_href: str | None = None,
        background_color: str | None = None,
        piano_html: str | None = None,
    ) -> str:
        out = ''
        if title is not None:
            out += f"<div style='font-size: 1em; font-weight: bold' class='card_title'>{title}</div>\n"
        if subtitle is not None:
            out += f"<div style='margin-top: -0.2em;font-size: 0.8em' class='card_subtitle'>{subtitle}</div>\n"
        out = f'''
        <div
            class='card_header'
            style='
                height: 32px;
                font-family: sans-serif;
            '
        >
        {out}
        </div>
        '''

        if header_href is not None:
            out = f'''
            <a href='{header_href}'>
            {out}
            </a>
            '''
        if piano_html is not None:
            out = f'''
            {out}
            {piano_html}
            '''

        background_color = f'background-color: {background_color};' if background_color is not None else ''

        classes = ' '.join(('card', *html_classes))
        out = f'''
        <div
            class='{classes}'
            style='
                margin: 5px;
                width: fit-content;
                padding: 0px 2px 0px 2px;
                border: 1px solid rgba(0,0,0,0.5);
                height: 120px;
                box-shadow: 2px 2px;
                border-radius: 3px;
                {background_color}
            '
        >
        {out}
        </div>
        '''
        return out

    @abc.abstractmethod
    def _repr_html_(
        self,
        html_classes: tuple[str, ...] = (),
        title: str | None = None,
        subtitle: str | None = None,
        header_href: str | None = None,
        background_color: str | None = None,
        noterange: NoteRange | None = None,
    ) -> str:
        ...
