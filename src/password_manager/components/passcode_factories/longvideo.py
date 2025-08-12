import random
from collections.abc import Callable

from nicegui import ui

from password_manager.types import Passcode, PasscodeInput

MAX_PASSCODE_BYTE_LIMIT = 20


class Timestamp:
    def __init__(self, hour: int, minute: int, second: int) -> None:
        """Timestamp class to help see if user input matches."""
        self.hour = hour
        self.minute = minute
        self.second = second

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Timestamp):
            return NotImplemented

        if other.hour == self.hour and other.minute == self.minute and other.second == self.second:
            return True
        else:
            return False

    def to_passcode(self) -> Passcode:
        """Turn the timestamp into a passcode value"""
        value = self.hour + self.minute + self.second
        return value.to_bytes(byteorder="big", length=MAX_PASSCODE_BYTE_LIMIT)


class LongVideoLock(PasscodeInput):
    @staticmethod
    def get_name() -> str:
        return "Long Video"

    def __init__(self, on_submit: Callable[[bytes], None], submit_text: str) -> None:
        """Long video lock that user needs to find a specific timestamp to unlock."""

        self.submit_passcode = on_submit
        # Internals for checking if user entered the correct timestamp
        self.correct_timestamps = [
            Timestamp(0, 20, 16),
            Timestamp(0, 56, 10),
            Timestamp(1, 27, 14),
            Timestamp(1, 57, 28),
            Timestamp(2, 16, 52),
            Timestamp(2, 24, 26),
            Timestamp(2, 40, 51),
            Timestamp(3, 7, 7),
            Timestamp(3, 59, 15),
            Timestamp(4, 0, 0),
            Timestamp(4, 59, 50),
            Timestamp(6, 5, 44),
            Timestamp(6, 19, 19),
            Timestamp(6, 28, 43),
            Timestamp(6, 50, 13),
            Timestamp(7, 4, 25),
        ]
        self.timestamp_n, self.timestamp_s = self._get_random_timestamp()
        self.user_timestamp = Timestamp(0, 0, 0)

        # Element with video and prompt for user input
        with ui.column():
            with ui.row():
                ui.html("""
                    <iframe width="560" height="315" src="https://www.youtube.com/embed/J-Vv-M0tWic?si=xLFP2Y0-VKNK0Edq"
                    title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write;
                    encrypted-media; gyroscope; picture-in-picture; web-share"
                    referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
                    """)
            with ui.row():
                ui.label(text=f"Enter the timestamp for the {self.timestamp_s} sound")
            with ui.row():
                with ui.column():
                    ui.number(label="Hour:", on_change=lambda e: self._update_user_hour_input(e.value))
                with ui.column():
                    ui.number(label="Minute:", on_change=lambda e: self._update_user_minute_input(e.value))
                with ui.column():
                    ui.number(label="Second:", on_change=lambda e: self._update_user_second_input(e.value))

        self.unlock_button = ui.button(submit_text, on_click=lambda: self._handle_unlock())

    def _get_random_timestamp(self) -> None:
        """Get a random number between 0 and the number of timestamps
        and return the number and it's ordinal string representation.
        """
        rand_n = random.randint(0, len(self.correct_timestamps))
        n = rand_n + 1

        # Get the ordinal string representation
        if 10 <= n % 100 <= 13:
            suffix = "th"
        else:
            # Get the last digit
            last_digit = n % 10
            if last_digit == 1:
                suffix = "st"
            elif last_digit == 2:
                suffix = "nd"
            elif last_digit == 3:
                suffix = "rd"
            else:
                suffix = "th"

        return rand_n, f"{n}{suffix}"

    def _update_user_hour_input(self, new_hour: int) -> None:
        """Update that user input."""
        self.user_timestamp.hour = int(new_hour)

    def _update_user_minute_input(self, new_minute: int) -> None:
        """Update that user input."""
        self.user_timestamp.minute = int(new_minute)

    def _update_user_second_input(self, new_second: int) -> None:
        """Update that user input."""
        self.user_timestamp.second = int(new_second)

    def _handle_unlock(self) -> None:
        """Handles the event of user pressing unlock button."""
        passcode = self.user_timestamp.to_passcode()
        self.submit_passcode(passcode)
