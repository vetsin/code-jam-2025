"""Functionality for generating passcode inputs.

We expose the type `PasscodeInputFactory` that defines a function used to generate
passcode inputs. All other public members in this module are functions of this type.
"""

from password_manager.components.passcode_factories.anagram import AnagramLock
from password_manager.components.passcode_factories.binary import BinaryInput
from password_manager.components.passcode_factories.longvideo import LongVideoLock
from password_manager.components.passcode_factories.map import MapLock
from password_manager.components.passcode_factories.text import TextInput
from password_manager.components.passcode_factories.typst import TypstInput
from password_manager.components.passcode_factories.snake import SnakeInput
from password_manager.types import PasscodeInput

ALL_PASSCODE_INPUTS: list[type[PasscodeInput]] = [
    AnagramLock,
    BinaryInput,
    LongVideoLock,
    MapLock,
    TextInput,
    TypstInput,
    SnakeInput,
]
"""All factories with an identifying name."""
