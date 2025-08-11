from nicegui import ui
from collections.abc import Callable
from password_manager.components.passcode_factories import ALL_FACTORIES, Passcode, PasscodeInputFactory


PASSWORD_SECTION_LABEL = "Password"


class PasswordSubmitterWide:
    def __init__(self, on_set_passcode: Callable[[Passcode], None]):
        self.set_passcode = on_set_passcode
        self.__make_ui()

    def __make_ui(self) -> None:
        with ui.card():
            ui.label(PASSWORD_SECTION_LABEL)
            tabs = self.__make_password_input_tabs()
            self.__make_tab_contents(tabs)

    def __make_tab_contents(self, tabs: list[ui.tab]) -> None:
        with ui.tab_panels(tabs, value=ALL_FACTORIES[0][0]).classes("w-full"):
            for name, factory in ALL_FACTORIES:
                self.__make_tab_content(name, factory)

    def __make_tab_content(self, name: str, factory: PasscodeInputFactory) -> None:
        with ui.tab_panel(name):
            factory(self.set_passcode)

    def __make_password_input_tabs(self) -> list[ui.tab]:
        with ui.tabs().classes("w-full") as tabs:
            for password_input in ALL_FACTORIES:
                ui.tab(password_input[0])

        return tabs
