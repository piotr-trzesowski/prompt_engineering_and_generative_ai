from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable


class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)
    NONE = (0, 0)

    @property
    def dx(self) -> int:
        return int(self.value[0])

    @property
    def dy(self) -> int:
        return int(self.value[1])


@dataclass(frozen=True, slots=True)
class GridPos:
    x: int
    y: int

    def moved(self, direction: Direction, steps: int = 1) -> GridPos:
        return GridPos(self.x + direction.dx * steps, self.y + direction.dy * steps)


@dataclass(slots=True)
class Entity:
    pos: GridPos
    direction: Direction


@dataclass(slots=True)
class Pacman(Entity):
    desired_direction: Direction
    lives: int


@dataclass(slots=True)
class Ghost(Entity):
    ghost_id: str
    spawn_pos: GridPos
    home_pos: GridPos


@dataclass(slots=True)
class Level:
    width: int
    height: int
    walls: frozenset[GridPos]
    pellets: set[GridPos]
    power_pellets: set[GridPos]
    pacman_spawn: GridPos
    ghost_spawns: dict[str, GridPos]
    ghost_home: GridPos
    scatter_targets: dict[str, GridPos]

    def in_bounds(self, pos: GridPos) -> bool:
        return 0 <= pos.x < self.width and 0 <= pos.y < self.height

    def is_wall(self, pos: GridPos) -> bool:
        return pos in self.walls

    def neighbors_4(self, pos: GridPos) -> Iterable[GridPos]:
        for d in (Direction.UP, Direction.LEFT, Direction.DOWN, Direction.RIGHT):
            yield pos.moved(d)


@dataclass(frozen=True, slots=True)
class GhostView:
    ghost_id: str
    pos: GridPos
    mode: str


@dataclass(frozen=True, slots=True)
class GameSnapshot:
    width: int
    height: int
    walls: frozenset[GridPos]
    pellets: frozenset[GridPos]
    power_pellets: frozenset[GridPos]
    pacman_pos: GridPos
    pacman_direction: Direction
    lives: int
    ghosts: tuple[GhostView, ...]
    score: int
    mode: str
    frightened_left: float
    game_over: bool
    level_complete: bool


@dataclass(slots=True)
class GameState:
    level: Level
    pacman: Pacman
    ghosts: dict[str, Ghost]
    score: int
    lives: int
    game_over: bool
    level_complete: bool
    frightened_left: float
