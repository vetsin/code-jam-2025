"""Functionality for generating passcode inputs.

We expose the type `PasscodeFactory` that defines a function used to generate
passcode inputs. All other public members in this module are functions of this type.
"""

from collections.abc import Callable

import nicegui

__all__ = [
    "PasscodeFactory",
]

# TODO: does it make more sense to define what a passcode element is here, or where we use it?
type PasscodeFactory = Callable[[Callable[[], None], Callable[[], None]], nicegui.ui.element]
"""A function that creates a passcode input.

It must take two arguments, `success: Callable[[], None]` and `failure: Callable[[], None]`.
It must return a nicegui element that calls `success()` every successful passcode input and
`failure()` every failed passcode input.
"""
