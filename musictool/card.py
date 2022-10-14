import abc


class CardMixin(abc.ABC):
    @staticmethod
    def repr_card(
        html_classes: tuple[str, ...] = ('card',),
        title: str | None = None,
        subtitle: str | None = None,
        header_href: str | None = None,
        piano_html: str | None = None,
    ) -> str:
        out = ''
        if title is not None:
            out += f"<h3 style='height:1em;' class='card_title'>{title}</h3>\n"
        if subtitle is not None:
            # out += f"<span style='margin-top: -0.2em; font-size: 0.8em' class='card_subtitle'>{subtitle}</span>\n"
            out += f"<div style='margin-top: -0.25em' class='card_subtitle'>{subtitle}</div>\n"
        out = f'''
        <div
            class='card_header'
            style='
                height: 32px;
                margin: -1em 0em 0em 0em;
            '
        >
        {out}
        </div>
        '''
        # margin-top: -25px;

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

        classes = ' '.join(html_classes)
        # padding: 10px;
        out = f'''
        <div 
            class='{classes}'
            style='
                margin: 5px;
                padding: 0px 2px 0px 2px;
                border: 1px solid rgba(0,0,0,0.5);
                width: 258px;
                height: 120px;
                box-shadow: 2px 2px;
                border-radius: 3px;
            '
        >
        {out}
        </div>
        '''
        return out

    @abc.abstractmethod
    def _repr_html_(
        self,
        html_classes: tuple[str, ...] = ('card',),
        title: str | None = None,
        subtitle: str | None = None,
        header_href: str | None = None,
    ):
        ...
