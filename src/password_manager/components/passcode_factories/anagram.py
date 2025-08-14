import random
from collections.abc import Callable

import requests
from nicegui import ui

from password_manager.types import Passcode, PasscodeInput


RANDOM_WORD_API_URL = "https://random-word-api.herokuapp.com/word"


class AnagramLock(PasscodeInput):
    @staticmethod
    def get_name() -> str:
        return "Anagram"

    def __init__(self, on_submit: Callable[[bytes], None], submit_text: str) -> None:
        """Anagram that the user needs to decode."""

        self.submit_passcode = on_submit
        # Internals for checking if user entered the correct password
        self.original_word = self._get_random_word()
        self.anagram = self._get_anagram_of_word()
        self.user_input = None

        # Element with Anagram and prompt for user input
        with ui.column():
            with ui.row(), ui.card():
                ui.label(text=f"Anagram: {self.anagram}")
            with ui.row(), ui.card():
                ui.input(label="Answer:", on_change=lambda e: self._update_user_input(e.value))

        self.unlock_button = ui.button(submit_text, on_click=lambda: self._handle_unlock())

    def _get_random_word(self) -> str:
        """Uses an API to get a random word with a length between 5 and 7 letters."""
        min_length = 5
        max_length = 7

        # Get a random number between 5 and 7, silence the linter warning because this is a game
        word_length = random.randint(min_length, max_length)  # noqa: S311

        url = f"{RANDOM_WORD_API_URL}?length={word_length}"

        try:
            # Make the API request
            response = requests.get(url, timeout=5)
            response.raise_for_status()

            # Get the word and return if valid
            word = response.json()
            if word and len(word) > 0:
                return word[0]

        except requests.exceptions.Timeout:
            print("Request timed out - API took too long")
            return "error"
        except requests.exceptions.RequestException as e:
            print(f"Error getting word from API: {e}")
            return "error"

        return "error"

    def _get_anagram_of_word(self) -> str:
        """Returns an anagram of the current word."""
        letters = list(self.original_word)
        random.shuffle(letters)
        return "".join(letters)

    def _update_user_input(self, new_input: str) -> None:
        """Update that user input."""
        if new_input:
            self.user_input = new_input

    def _handle_unlock(self) -> None:
        """Handles the event of user pressing unlock button."""
        if self.original_word.lower() == self.user_input.lower():
            # User got it right
            self.submit_passcode(bytes([1]))
        else:
            # User got it wrong
            self.submit_passcode(bytes([0]))
