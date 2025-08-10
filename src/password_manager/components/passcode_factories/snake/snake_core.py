from __future__ import annotations

import collections
import random
from enum import IntEnum
import time
from typing import TYPE_CHECKING

from nicegui import ui

from password_manager.components.passcode_factories.snake.vec2 import Vec2

if TYPE_CHECKING:
    from collections.abc import Callable

    from password_manager.components.passcode_factories import Passcode


class Direction(IntEnum):
    """A move direction in snake."""

    LEFT = 0b00
    RIGHT = 0b01
    UP = 0b10
    DOWN = 0b11


MAX_PASSCODE_BYTE_LIMIT = 40


class SnakeInvariantError(Exception):
    """Snake's internal state violated an invariant."""


class Snake:
    """The classic game Snake.

    We allow the user to change the current direction and advance the game state by one unit (a tick).
    """

    # Invariants
    #
    # Before and after every method call (including private), unless specified, these must be true:
    # - self._available_food_pos is correct
    #   - i.e. all tiles not holding a food or snake tile are in that set
    # - self._map correctly represents the map
    #   - the map is defined as well by the snake and food.

    GROUND = " "
    SNAKE = "o"
    FOOD = "."

    def __init__(
        self, size: int, start: tuple[int, int], direction: Direction, seed: str, debug: bool = False
    ) -> None:
        if not all(0 <= coord < size for coord in start):
            err = f"start must be within the board with size {size}"
            raise ValueError(err)

        if size <= 1:
            err = "map size must be at least 2."
            raise ValueError(err)

        self._starting_args = (size, start, direction, seed, debug)

        self.debug = debug
        """Whether debug assertions are enabled."""

        self._size = size
        """Side length of square board"""

        self._dead = False
        """Whether the snake is dead."""

        self._moves: int = 0
        """Binary representation of the moves we've taken."""

        self._curr_move: int = 0
        """The current move we're on, 0-indexed.

        Since `Direction`s are two bits wide, the amount we need to shift to encode the next move
        is `self._curr_move * 2`.
        """

        self._snake: collections.deque[Vec2] = collections.deque([Vec2(start[0], start[1])])
        """A buffer of (i, j) tuples that make up the snake.

        Right side is head, left side is tail.
        """

        self._snake_direction: Direction = direction
        """Direction the snake will move next tick."""

        self._map: list[list[str]] = [[Snake.GROUND] * size for _ in range(size)]
        self._map[start[0]][start[1]] = Snake.SNAKE

        self._rng = random.Random(seed)  # noqa: S311

        self._available_food_pos: set[Vec2] = set()
        """Positions open for food to be placed"""
        for i in range(size):
            for j in range(size):
                self._available_food_pos.add(Vec2(i, j))
        self._available_food_pos.remove(self._snake[-1])

        # just trying here to have food pos not overlap the snake because
        # that's probably an invariant that shouldn't be violated
        self._food_pos: Vec2
        self._spawn_food()

        if debug:
            self._check_invariants()

    @staticmethod
    def replay_from_bytes(
        directions: bytes,
        size: int,
        start: tuple[int, int],
        direction: Direction,
        seed: str,
        log_ticks_with_delay: float | None = None,
    ) -> None:
        """Replay a game from a byte string of moves, with debug on.

        Can be used for checking if a replay file is valid. Since debug is on, if a invalid game state is
        encountered, we error.

        If `log_ticks_with_delay` is some `delay: float`, log map every tick to stdout with that delay.
        """

        dirs_int: int = int.from_bytes(directions)  # hope byteorder is correct
        curr_move_mask = 0b11
        level = 0
        snake = Snake(size, start, direction, seed, debug=True)
        LEVEL_LEN = 2
        BIT_PER_BYTE = 8
        while level < len(directions) * BIT_PER_BYTE:
            if log_ticks_with_delay is not None:
                print(snake.map_as_str())
                time.sleep(log_ticks_with_delay)
            move = (curr_move_mask & dirs_int) >> level
            dir = Direction(move)
            snake.change_direction(dir)
            try:
                snake.tick()
            except SnakeInvariantError as e:
                print(snake.map_as_str())
                raise e
            curr_move_mask <<= 2
            level += 2

    def _map_from_data(self) -> str:
        """Slowly reconstruct the map from our interior data.

        This is reference implementation for `map_as_str`.
        """
        map_: list[list[str]] = [[Snake.GROUND] * self._size for _ in range(self._size)]
        for i, j in self._snake:
            map_[i][j] = Snake.SNAKE

        i, j = self._food_pos
        map_[i][j] = Snake.FOOD

        return Snake._a_map_as_str(self._size, map_)

    def reset(self) -> None:
        """Reset the game."""
        self.__init__(*self._starting_args)

    def _spawn_food(self) -> None:
        """Spawn a food somewhere based on what tiles are available.

        We have one food per game, so assume the food is already conceptually "removed".
        This can mean in available_food_pos, or not and covered by a snake tile.

        `IndexError`s from rand.choice if there are no available tiles.
        """
        next_food_pos = self._rng.choice(list(self._available_food_pos))
        self._available_food_pos.remove(next_food_pos)

        self._map[next_food_pos[0]][next_food_pos[1]] = Snake.FOOD
        self._food_pos = next_food_pos

    def change_direction(self, move: Direction) -> None:
        """Signal to the engine that we want the snake to turn in `Move` direction next tick."""
        self._snake_direction = move

    def tick(self) -> bool:
        """Advance the game state by one unit. Return whether the game has ended after the tick.

        No map state is changed if the game has already ended.

        Our snake game is a very simple variant.
        - if we will eat food, spawn new food
        - else, pop tail
        - then, move the head
        - repeat
        """
        if self._dead:
            return True

        self._moves |= self._snake_direction << self._curr_move * 2

        next_head: Vec2 = self._snake[-1]
        match self._snake_direction:
            case Direction.LEFT:
                next_head += Vec2(0, -1)
            case Direction.RIGHT:
                next_head += Vec2(0, 1)
            case Direction.UP:
                next_head += Vec2(-1, 0)
            case Direction.DOWN:
                next_head += Vec2(1, 0)
        next_head %= self._size  # wrap around.

        if next_head == self._food_pos:
            # if we will eat food, spawn new food
            try:
                self._spawn_food()
            except IndexError:
                self._dead = True
        else:
            # else, pop tail
            prev_tail = self._snake.popleft()
            self._available_food_pos.add(prev_tail)
            self._map[prev_tail[0]][prev_tail[1]] = Snake.GROUND

        if next_head in self._snake:
            self._dead = True
            return self._dead

        # then, move the head
        self._snake.append(next_head)
        self._available_food_pos.discard(next_head)  # nothing to discard if just ate

        self._map[next_head[0]][next_head[1]] = Snake.SNAKE

        self._curr_move += 1

        if self.debug:
            self._check_invariants()
        return self._dead

    def _check_invariants(self) -> None:
        print(f"avail: {self._available_food_pos}")
        print(f"snake: {self._snake}")
        print(f"curr food: {self._food_pos}")
        all_tiles: set[Vec2] = self._available_food_pos.union((self._food_pos,), self._snake)
        print(f"all tiles: {sorted(list(all_tiles))}")
        if len(all_tiles) != self._size**2:
            raise SnakeInvariantError(f"available food positions not exhaustive.")

        if any([any([coord < 0 or coord >= self._size for coord in tile]) for tile in all_tiles]):
            raise SnakeInvariantError(f"available food positions out of bound.")

        shown_to_user = self.map_as_str()
        ref_impl = self._map_from_data()
        if shown_to_user != ref_impl:
            raise SnakeInvariantError(
                f"internal state inconsistent.\n\ncomparing \n\nuser:\n{shown_to_user}\n\ninterior:\n{ref_impl}"
            )

    @staticmethod
    def _a_map_as_str(size: int, map: list[list[str]]) -> str:
        """Render a generic map."""
        top_bot_border = " " + "-" * size + "\n"
        side_border = "|"
        return (
            top_bot_border
            + "\n".join([side_border + "".join(line) + side_border for line in map])
            + "\n"
            + top_bot_border
        )

    def map_as_str(self) -> str:
        """Return the game's map as a string."""
        return Snake._a_map_as_str(self._size, self._map)

    def moves_as_bytes(self) -> bytes:
        return self._moves.to_bytes(byteorder="big", length=MAX_PASSCODE_BYTE_LIMIT)

    def moves_as_passcode(self) -> Passcode:
        """Return the moves we took as a passcode."""
        return self.moves_as_bytes()


def snakeinput_factory(submit_passcode: Callable[[Passcode], None]) -> ui.element:
    """Snake."""
    snake = Snake(size=4, start=((2, 2)), direction=Direction.UP, seed="TEMP, expose this as arg to user?")

    with ui.column() as snakeinput:
        # https://fsymbols.com/signs/arrow/ copy pasted unicode from here
        with ui.button_group():
            ui.button("🡸", on_click=lambda: snake.change_direction(Direction.LEFT))
            ui.button("🡻", on_click=lambda: snake.change_direction(Direction.DOWN))
            ui.button("🡹", on_click=lambda: snake.change_direction(Direction.UP))
            ui.button("🡺", on_click=lambda: snake.change_direction(Direction.RIGHT))

        map = ui.code()

    # TICK_INTERVAL = 0.7  # noqa: N806
    TICK_INTERVAL = 1  # noqa: N806
    """Time between snake ticks"""
    WAIT_INTERVAL = 2.5  # noqa: N806
    """Time between games when player died."""

    # we use this list as an address, basically. because python doesn't have address-of.
    # we assert it always has exactly one item.
    timer: list[ui.timer] = []

    def tick_and_submit() -> None:
        """Tick game, submit and reset game if it ended."""
        game_end = snake.tick()
        map.set_content(snake.map_as_str())
        if game_end:
            submit_passcode(snake.moves_as_passcode())
            assert len(timer) == 1  # noqa: S101
            timer[0].cancel()
            timer.pop()
            snake.reset()
            ui.timer(
                interval=WAIT_INTERVAL,
                callback=lambda: timer.append(ui.timer(interval=TICK_INTERVAL, callback=tick_and_submit)),
                once=True,
            )

    timer.append(ui.timer(interval=TICK_INTERVAL, callback=tick_and_submit))

    return snakeinput
