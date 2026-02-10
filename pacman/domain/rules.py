from __future__ import annotations

from dataclasses import dataclass

from pacman.domain.model import Direction, GameState, GridPos


PELLET_SCORE = 10
POWER_PELLET_SCORE = 50
GHOST_EATEN_SCORE = 200


@dataclass(frozen=True, slots=True)
class PelletResult:
    pellet_eaten: bool
    power_eaten: bool
    score_delta: int


def wrap_tunnel(level_width: int, pos: GridPos) -> GridPos:
    # Optional tunnel: wrap left/right edges.
    if pos.x < 0:
        return GridPos(level_width - 1, pos.y)
    if pos.x >= level_width:
        return GridPos(0, pos.y)
    return pos


def can_move(level: "object", from_pos: GridPos, direction: Direction) -> bool:
    nxt = from_pos.moved(direction)
    nxt = wrap_tunnel(getattr(level, "width"), nxt)
    if not getattr(level, "in_bounds")(nxt):
        return False
    return not getattr(level, "is_wall")(nxt)


def apply_pellet_rules(state: GameState) -> PelletResult:
    pos = state.pacman.pos
    score = 0
    pellet = False
    power = False

    if pos in state.level.pellets:
        state.level.pellets.remove(pos)
        score += PELLET_SCORE
        pellet = True

    if pos in state.level.power_pellets:
        state.level.power_pellets.remove(pos)
        score += POWER_PELLET_SCORE
        power = True

    state.score += score
    if not state.level.pellets and not state.level.power_pellets:
        state.level_complete = True

    return PelletResult(pellet_eaten=pellet, power_eaten=power, score_delta=score)


def manhattan(a: GridPos, b: GridPos) -> int:
    return abs(a.x - b.x) + abs(a.y - b.y)

