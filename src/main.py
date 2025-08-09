from nicegui import ui

from password_manager import app

app.app()

if __name__ in {"__main__", "__mp_main__"}:
    ui.run()
