from nicegui import ui

from password_manager.passcode_factories import *  # noqa: F403

login_container = ui.column().classes("self-center")


def add() -> None:
    """Add a removable card to the login container.

    This is just me testing out cool test code. Neat that this works.
    """
    with login_container, ui.card() as card:
        # Header with title and close button
        with ui.row().classes("w-full justify-between items-center mb-2"):
            ui.label("title").classes("text-lg font-semibold")
            ui.button(icon="close", on_click=lambda: card.delete()).props("flat round size=sm").classes(
                "text-gray-500 hover:text-gray-700",
            )

        # Card content
        ui.label("content")


def item_to_spawn_new_passcode() -> None:
    """Just a placeholder.

    This should probably be in `password_manager` and take a password_factories.PasscodeFactory
    and return a ui.item that on click, spawns the passcode.
    """
    ui.item("temp", on_click=lambda: ui.notify("You clicked the temp thing."))


with login_container:
    ui.label("What kind of passcode?")

    with ui.dropdown_button("Open me!", auto_close=True):
        # for each passcode_factory in password_manager.passcode_factories,
        #     item_to_spawn_new_passcode(passcode_factory) ig
        item_to_spawn_new_passcode()
        ui.item("add a thing", on_click=add)
        ui.item("Item 2", on_click=lambda: ui.notify("You clicked item 2"))


ui.run()
