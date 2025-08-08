"""Functionality for generating passcode inputs.

We expose the type `PasscodeInputFactory` that defines a function used to generate
passcode inputs. All other public members in this module are functions of this type.
"""

from collections.abc import Callable

import nicegui

__all__ = [
    "PasscodeInputFactory",
]

type Passcode = int

# TODO: does it make more sense to define what a passcode element is here, or where we use it?
type PasscodeInputFactory = Callable[[Callable[[Passcode], None]], nicegui.ui.element]
"""A function that creates a passcode input.

It must take the argument `submit_passcode: Callable[[Passcode], None]`.
It must return a nicegui element that calls `submit_passcode` every passcode input.
The user of this passcode input decides whether it succeeded or failed.
"""
