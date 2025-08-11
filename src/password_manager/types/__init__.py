"""Global types that are often used."""

from abc import ABC, abstractmethod
from collections.abc import Callable


class Component(ABC):
    """The abstract base class for a component.

    You may want to implement `Component`. The relevant section is below.

    # What is a `Component`

    A `Component` is just a reusable bit of UI. You can think of it like
    a way to create an HTML container that you have named. The name and
    concept come from React's Components.

    A `Component` can be understood as a noun: a declarative way to say
    "I want this component to be here in the app."

    It can also be understood as a verb: an imperative command to create
    this component in the current context. (Note: `with` is called a context
    manager.)

    For example, if you see code like:

    ```python
    class Item(Component): ...

    with ui.column():
        Item("hello")
        Item("world!")
        Item(":-)")
    ```

    Using declarative nouns, you can think "My ui has a column of three `Item`s."

    Using imperative verbs, you can think "Create a context with a column. In that
    context, spawn three `Item`s."

    For more (code) examples, see the other files in this directory.

    # Implementing `Component`

    To implement a Component, just define an `__init__` that spawns at least
    one `nicegui.ui.element`.

    For example,

    ```python
    class DoubleLabel(Component):
        def __init__(self, text: str) -> None:
            ui.label(text)
            ui.label(text)
    ```

    # Why is this a class?

    A class that only requires an `__init__`? Many of these "components" could
    just be functions!

    Yes, this is true. But it's just better semantically and for IDE support
    this way. If we defined `type Component = Callable[Any, Any]`, there's no
    way to tag components with their type. i.e., you can't say "this function also
    has type `Component`." But by subclassing, any implementor clearly is-a
    `Component`! People unfamiliar with the code base will be able to see
    this and know what type the class is associated with. They can also jump to
    or read this documentation for what a `Component` is via their IDE.

    Components as functions is also odd because functions are semantically verbs,
    while objects are semantically nouns. Components as functions might have to be
    verbosely named `spawn_component` instead of `Component` to make semantic sense.
    """

    @abstractmethod
    def __init__(self) -> None:
        """Spawn a `Component`."""


type Passcode = bytes


class PasscodeInput(Component, ABC):
    """The abstract base class for a passcode input method.

    To implement a PasscodeInput as a subclass, you must
    - Spawn some NiceGUI element that implements its own submit mechanism.
    - If the submit mechanism can be labeled, it must be labeled `submit_text`
      (if we are logging in the user, we might want the label to be "log in," and if we're
      registering a new user, we might want the label to be "sign up").
    - Your code must call `on_submit(passcode)` whenever its submit mechanism is triggered.

    For a simple example, a PasscodeInput could be a text box with a submit button. It would
    set the submit button's label to `submit_text`, and call `on_submit` with the
    contents of the text box when the button is pressed.

    For a sillier example, a PasscodeInput could be a snake game. It would call `on_submit`
    with the history of snake moves when the game ends. The submit mechanism (ending the game)
    is not labeled, so we ignore the parameter.

    For more (code) examples, see the other files in this directory.
    """

    @abstractmethod
    def __init__(self, on_submit: Callable[[Passcode], None], submit_text: str) -> None:
        """Spawn a PasscodeInput."""
