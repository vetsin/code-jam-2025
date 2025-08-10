from collections.abc import Callable

from nicegui import ui

from password_manager.components.passcode_factories import Passcode, PasscodeInputFactory
from password_manager.components.passcode_factories.anagram import anagraminput_factory
from password_manager.components.passcode_factories.binary import binaryinput_factory
from password_manager.components.passcode_factories.map import map_input_factory
from password_manager.components.passcode_factories.snake import snakeinput_factory
from password_manager.components.passcode_factories.text import textinput_factory
from password_manager.components.passcode_factories.typst import typstinput_factory


def login(submit_passcode: Callable[[Passcode], None]) -> ui.element:
    """Component for logging in.

    - We have a dropdown to select passcode inputs from `passcode_factories`.
    - When we select an input type from the dropdown, we spawn the corresponding passcode input.
    - Multiple inputs can be active at a time.
        - If we don't like this, we might refactor so that only one input is active at a time.
          If another is selected, we despawn the old input before spawning the new input.
    - Like the individual inputs, we defer the decision on whether an input succeeded or failed
      to our caller. To do so, we forward our `submit_passcode` function into the spawned input.
    """
    with ui.column() as login, ui.dropdown_button("Open me!", auto_close=True) as dropdown:

        def _add(elem: Callable[[], ui.element]) -> None:
            """Spawn an element into login wrapped in a closable card."""
            with login, ui.card() as card, ui.row().classes("w-full justify-between items-center mb-2"):
                elem()
                ui.button(icon="close", on_click=lambda: card.delete()).props("flat round size=sm").classes(
                    "text-gray-500 hover:text-gray-700",
                )

        def _spawn_new_passcode_as_item(
            name: str,
            spawn_pcode_input: PasscodeInputFactory,
            submit_passcode: Callable[[Passcode], None],
        ) -> None:
            """Spawn a passcode as a named item into the dropdown. It should create a new passcode on select."""
            with dropdown:
                ui.item(name, on_click=lambda: _add(elem=lambda: spawn_pcode_input(submit_passcode)))

        _spawn_new_passcode_as_item("Text Input", textinput_factory, submit_passcode)
        _spawn_new_passcode_as_item("Binary Input", binaryinput_factory, submit_passcode)
        _spawn_new_passcode_as_item("Typst Input", typstinput_factory, submit_passcode)
        _spawn_new_passcode_as_item("Map Input", map_input_factory, submit_passcode)
        _spawn_new_passcode_as_item("Snake Input", snakeinput_factory, submit_passcode)
        _spawn_new_passcode_as_item("Anagram Input", anagraminput_factory, submit_passcode)
        # spawn more input types as we code them

    return login
