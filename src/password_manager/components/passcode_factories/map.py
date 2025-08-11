from collections.abc import Callable
from struct import pack

from nicegui import events, ui

from password_manager.types import PasscodeInput, Passcode


MARKER_AT_ZERO_ERROR = "Marker cannot be at 0x0"


class MapLock(PasscodeInput):
    @staticmethod
    def get_name() -> str:
        return "Map"

    def __init__(self, on_submit: Callable[[bytes], None], submit_text: str) -> None:
        """See https://github.com/vetsin/code-jam-2025/issues/6."""
        self.submit_passcode = on_submit

        self.map = ui.leaflet(center=(51.505, -0.090), zoom=3)
        self.map.on("map-click", self.__on_map_input)

        self.marker = self.map.marker(latlng=(0, 0))
        self.latitude = 0
        self.longitude = 0

        self.unlock_button = ui.button(submit_text, on_click=lambda: self.__handle_unlock())

    def __handle_unlock(self) -> None:
        try:
            value = self.__get_passcode_from_placement()
            self.submit_passcode(value)
        except (ValueError, TypeError):
            ui.notify("Please enter a valid place", color="negative")

    def __on_map_input(self, e: events.GenericEventArguments) -> None:
        self.latitude = e.args["latlng"]["lat"]
        self.longitude = e.args["latlng"]["lng"]
        self.__set_marker_to_location()

    def __set_marker_to_location(self) -> None:
        self.marker.move(self.latitude, self.longitude)

    def __get_passcode_from_placement(self) -> Passcode:
        if self.latitude == 0 and self.longitude == 0:
            raise ValueError(MARKER_AT_ZERO_ERROR)
        return pack(">ff", self.latitude, self.longitude)
