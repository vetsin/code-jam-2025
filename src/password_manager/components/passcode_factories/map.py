from collections.abc import Callable
from nicegui import ui

from . import Passcode


class MapLock:
    """See https://github.com/vetsin/code-jam-2025/issues/6."""

    def __init__(self, submit_passcode: Callable[[Passcode], None]):
        passcode_input = ui.number(label='Enter Passcode', format='0', step=1)

        ui.html('This is <u>emphasized</u>.', tag='em')

        def handle_submit():
            try:
                value = int(passcode_input.value)
                submit_passcode(value)
            except (ValueError, TypeError):
                ui.notify('Please enter a valid number', color='negative')

        ui.button('Unlock', on_click=handle_submit)

