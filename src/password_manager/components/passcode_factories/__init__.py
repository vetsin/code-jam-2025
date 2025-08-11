"""Functionality for generating passcode inputs.

We expose the type `PasscodeInputFactory` that defines a function used to generate
passcode inputs. All other public members in this module are functions of this type.
"""

from password_manager.components.passcode_factories.anagram import anagraminput_factory
from password_manager.components.passcode_factories.binary import binaryinput_factory
from password_manager.components.passcode_factories.map import map_input_factory
from password_manager.components.passcode_factories.text import textinput_factory
from password_manager.components.passcode_factories.typst import typstinput_factory
from password_manager.components.passcode_factories.snake import snakeinput_factory

ALL_FACTORIES: list[tuple[str, PasscodeInputFactory]] = [
    ("Anagram", anagraminput_factory),
    ("Binary", binaryinput_factory),
    ("Map", map_input_factory),
    ("Text", textinput_factory),
    ("Typst", typstinput_factory),
    ("Snake", snakeinput_factory),
]
"""All factories with an identifying name."""
