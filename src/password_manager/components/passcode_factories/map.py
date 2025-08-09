from collections.abc import Callable
from nicegui import events, ui
from struct import pack

from . import Passcode


class MapLock:
    """See https://github.com/vetsin/code-jam-2025/issues/6."""

    def __init__(self, submit_passcode: Callable[[Passcode], None]):
        self.submit_passcode = submit_passcode

        self.map = ui.leaflet(center=(51.505, -0.090), zoom=3)
        self.map.on("map-click", self.on_map_input)

        self.marker = self.map.marker(latlng=(0, 0))
        self.latitude = 0
        self.longitude = 0

        ui.button("Unlock", on_click=lambda: self.handle_unlock())

    def handle_unlock(self):
        try:
            value = self.get_passcode_from_placement()
            self.submit_passcode(value)
        except (ValueError, TypeError):
            ui.notify("Please enter a valid place", color="negative")

    def on_map_input(self, e: events.GenericEventArguments) -> None:
        self.latitude = e.args["latlng"]["lat"]
        self.longitude = e.args["latlng"]["lng"]
        self.set_marker_to_location()

    def set_marker_to_location(self):
        self.marker.move(self.latitude, self.longitude)

    def get_passcode_from_placement(self) -> Passcode:
        if self.latitude == 0 and self.longitude == 0:
            raise ValueError("Cannot be Zero")
        return pack(">ff", self.latitude, self.longitude)
