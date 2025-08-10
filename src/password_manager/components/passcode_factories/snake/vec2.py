from __future__ import annotations

from collections.abc import Iterator
from typing import Self


class Vec2(tuple[int, int]):
    """A 2d int vector made for snake."""

    __slots__ = ()

    def __new__(cls, a: int, b: int) -> Self:
        """Make a new Vec2."""
        return tuple.__new__(cls, (a, b))

    def __add__(self, other: Vec2) -> Vec2:
        return Vec2(self[0] + other[0], self[1] + other[1])

    def __mod__(self, other: int) -> Vec2:
        return Vec2(self[0] % other, self[1] % other)

    def __eq__(self, other: Vec2) -> bool:
        return self[0] == other[0] and self[1] == other[1]

    def __hash__(self) -> int:
        return hash((self[0], self[1]))

    def __str__(self) -> str:
        return f"vec2({self[0]}, {self[1]})"

    def __iter__(self) -> Iterator[int]:
        return super().__iter__()

    def __tuple__(self) -> tuple[int, int]:
        return (self[0], self[1])


if __name__ == "__main__":
    # okay couldn't be bothered to figure out how to put unit tests in this module so they're here for now.
    x = Vec2(10, 20)
    assert x + Vec2(1, 1) == Vec2(11, 21)  # noqa: S101
    assert x % 6 == Vec2(4, 2)  # noqa: S101

    x %= 6
    assert x == Vec2(4, 2)  # noqa: S101
