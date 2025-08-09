import functools
import subprocess
from collections.abc import Callable

from nicegui import run, ui

from . import Passcode


def str_to_passcode(s: str) -> Passcode:
    """Convert a str to a passcode."""
    return s.encode("utf-8")


def typstinput_factory(submit_passcode: Callable[[Passcode], None]) -> ui.element:
    """Typst input."""
    with ui.column() as typstinput:
        ui.codemirror(on_change=lambda e: _render_and_submit_passcode(e.value)).classes("w-64")
        svg = ui.html("")

        async def _render_and_submit_passcode(code: str) -> None:
            result = await run.cpu_bound(
                functools.partial(
                    subprocess.run,
                    [
                        "typst",
                        "compile",
                        "-",
                        "-",
                        "-f",
                        "svg",
                    ],
                    capture_output=True,
                    input=bytes("#set page(width: auto, height: auto, margin: 1em)\n" + code, "utf-8"),
                ),
            )
            try:
                result.check_returncode()
                output: bytes = result.stdout  # type: ignore  # mypy doesn't detect this correctly  # noqa: PGH003

                svg.set_content(output.decode("utf-8"))
                submit_passcode(output)
            except subprocess.CalledProcessError:
                print("typst errored")

    return typstinput
