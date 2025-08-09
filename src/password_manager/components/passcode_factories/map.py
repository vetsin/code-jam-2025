from collections.abc import Callable
from nicegui import events, ui

from . import Passcode

class MapLock:
    """See https://github.com/vetsin/code-jam-2025/issues/6."""

    def __init__(self, submit_passcode: Callable[[Passcode], None]):
        self.passcode_input = ui.number(label='Enter Passcode', format='0', step=1)

        self.map = ui.leaflet(center=(51.505, -0.090), zoom=3)
        self.marker = self.map.marker(latlng=(0, 0))
        self.map.on('map-click', self.on_map_input)

        ui.button('Unlock', on_click=self.handle_submit)

    def handle_submit():
        try:
            value = int(passcode_input.value)
            submit_passcode(value)
        except (ValueError, TypeError):
            ui.notify('Please enter a valid number', color='negative')
            
    def on_map_input(self, e: events.GenericEventArguments) -> None:
        latitude = e.args['latlng']['lat']
        longitude = e.args['latlng']['lng']
        self.set_marker_to_location(latitude, longitude)

    def set_marker_to_location(self, latitude: float, longitude: float):
        self.marker.move(latitude, longitude)

