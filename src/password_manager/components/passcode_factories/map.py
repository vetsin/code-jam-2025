from collections.abc import Callable
from nicegui import events, ui

from . import Passcode

class MapLock:
    """See https://github.com/vetsin/code-jam-2025/issues/6."""

    def __init__(self, submit_passcode: Callable[[Passcode], None]):
        self.passcode_input = ui.number(label='Enter Passcode', format='0', step=1)

        self.map = ui.leaflet(center=(51.505, -0.090), zoom=3)
        self.map.on('map-click', self.on_map_click)

        ui.button('Unlock', on_click=self.handle_submit)

    def handle_submit():
        try:
            value = int(passcode_input.value)
            submit_passcode(value)
        except (ValueError, TypeError):
            ui.notify('Please enter a valid number', color='negative')

    def on_map_click(self, e: events.GenericEventArguments):
        lat = e.args['latlng']['lat']
        lng = e.args['latlng']['lng']
        self.map.marker(latlng=(lat, lng))
        self.map.on('map-click', handle_click)
