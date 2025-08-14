import random
from collections.abc import Callable

from nicegui import ui

from password_manager.types import Passcode, PasscodeInput


class GuesserLock(PasscodeInput):
    @staticmethod
    def get_name() -> str:
        return "Guesser"

    def __init__(self, on_submit: Callable[[bytes], None], submit_text: str) -> None:
        """Guesser that user needs to get right."""

        self.submit_passcode = on_submit
        # Internals for checking if user entered the correct password
        self.colors = [
            "",
            "red",
            "blue",
            "green",
            "yellow",
            "orange",
            "purple",
            "pink",
            "brown",
            "black",
            "white",
            "gray",
            "cyan",
            "magenta",
            "lime",
            "navy",
            "maroon",
            "olive",
            "teal",
            "silver",
            "gold",
            "coral",
            "salmon",
            "crimson",
            "indigo",
            "violet",
            "turquoise",
            "beige",
            "tan",
            "khaki",
            "plum",
            "orchid",
            "lavender",
            "mint",
            "peach",
            "apricot",
            "rose",
            "ruby",
            "emerald",
            "sapphire",
            "amber",
            "jade",
            "ivory",
            "pearl",
            "bronze",
            "copper",
            "steel",
            "slate",
            "charcoal",
            "scarlet",
            "burgundy",
        ]
        self.number = self._get_random_number()
        self.user_input_color = None
        self.user_input_number = None

        # Element with prompt for user input
        with ui.column():
            with ui.row(), ui.card():
                ui.label(text=f"Guess the color and number (1-50)")
            with ui.row(), ui.card():
                ui.input(label="Color:", on_change=lambda e: self._update_user_color(e.value))
            with ui.row(), ui.card():
                ui.input(label="Number:", on_change=lambda e: self._update_user_num(e.value))

        self.unlock_button = ui.button(submit_text, on_click=lambda: self._handle_unlock())

    def _get_random_number(self) -> int:
        """Returns a random number between 1 and 50"""
        min_number = 1
        max_number = 50

        # Get a random number between 1 and 7, silence the linter warning because this is a game
        num = random.randint(min_number, max_number)  # noqa: S311
        print(f"Guesser number is {num} and color is {self.colors[num]}")

        return num

    def _update_user_color(self, new_input: str) -> None:
        """Update user color."""
        if new_input:
            self.user_input_color = new_input

    def _update_user_num(self, new_input: int) -> None:
        """Update user number."""
        if new_input:
            self.user_input_number = new_input

    def _handle_unlock(self) -> None:
        """Handles the event of user pressing unlock button."""
        if self.user_input_color == self.colors[self.number] and self.user_input_number == self.number:
            # User got it right
            self.submit_passcode(bytes([1]))
        else:
            # User got it wrong
            self.submit_passcode(bytes([0]))
