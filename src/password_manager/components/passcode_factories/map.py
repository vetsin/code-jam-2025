from collections.abc import Callable
from nicegui import ui

from . import Passcode

MAP_SITE_SRC = "https://www.openstreetmap.org/export/embed.html?bbox=-0.510375,51.286760,0.334015,51.691874&layer=mapnik"
MAP_WIDTH = 600
MAP_HEIGHT = 400
MAP_SITE_IFRAME = f'<iframe src={MAP_SITE_SRC} \
  width="{MAP_WIDTH}" height="{MAP_HEIGHT}" \
  frameborder="0" style="border: 1px solid black;"> \
</iframe>'

class MapLock:
    """See https://github.com/vetsin/code-jam-2025/issues/6."""

    def __init__(self, submit_passcode: Callable[[Passcode], None]):
        self.passcode_input = ui.number(label='Enter Passcode', format='0', step=1)
        ui.html(MAP_SITE_IFRAME)
        ui.button('Unlock', on_click=self.handle_submit)

    def handle_submit():
        try:
            value = int(passcode_input.value)
            submit_passcode(value)
        except (ValueError, TypeError):
            ui.notify('Please enter a valid number', color='negative')


