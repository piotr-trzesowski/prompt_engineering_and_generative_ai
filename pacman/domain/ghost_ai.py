from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Protocol

from pacman.domain.model import Direction, GameState, Ghost, GridPos
from pacman.domain.rules import manhattan


class GhostMode(Enum):
    CHASE = "CHASE"
    SCATTER = "SCATTER"
    FRIGHTENED = "FRIGHTENED"
    EATEN = "EATEN"


class TargetStrategy(Protocol):
    def get_target(self, state: GameState, ghost_id: str) -> GridPos: ...


@dataclass(frozen=True, slots=True)
class BlinkyStrategy:
    def get_target(self, state: GameState, ghost_id: str) -> GridPos:
        return state.pacman.pos


@dataclass(frozen=True, slots=True)
class PinkyStrategy:
    ahead: int = 4

    def get_target(self, state: GameState, ghost_id: str) -> GridPos:
        d = state.pacman.direction
        if d == Direction.NONE:
            return state.pacman.pos
        return state.pacman.pos.moved(d, self.ahead)


@dataclass(frozen=True, slots=True)
class InkyStrategy:
    ahead: int = 2

    def get_target(self, state: GameState, ghost_id: str) -> GridPos:
        blinky = state.ghosts.get("blinky")
        pivot = state.pacman.pos.moved(state.pacman.direction, self.ahead)
        if blinky is None:
            return pivot
        vx = pivot.x - blinky.pos.x
        vy = pivot.y - blinky.pos.y
        return GridPos(pivot.x + vx, pivot.y + vy)


@dataclass(frozen=True, slots=True)
class ClydeStrategy:
    chase_distance: int = 8

    def get_target(self, state: GameState, ghost_id: str) -> GridPos:
        ghost = state.ghosts[ghost_id]
        if manhattan(ghost.pos, state.pacman.pos) > self.chase_distance:
            return state.pacman.pos
        return state.level.scatter_targets.get(ghost_id, state.pacman.pos)


@dataclass(slots=True)
class GhostBrain:
    ghost_id: str
    strategy: TargetStrategy
    mode: GhostMode

    def set_mode(self, mode: GhostMode) -> None:
        self.mode = mode

    def choose_dir(
        self,
        state: GameState,
        ghost: Ghost,
        valid_dirs: list[Direction],
        disallow_reverse: bool,
    ) -> Direction:
        if not valid_dirs:
            return Direction.NONE

        reverse = {
            Direction.UP: Direction.DOWN,
            Direction.DOWN: Direction.UP,
            Direction.LEFT: Direction.RIGHT,
            Direction.RIGHT: Direction.LEFT,
            Direction.NONE: Direction.NONE,
        }[ghost.direction]
        candidates = valid_dirs
        if disallow_reverse and len(candidates) > 1:
            candidates = [d for d in candidates if d != reverse] or valid_dirs

        if self.mode == GhostMode.FRIGHTENED:
            # Deterministic "flee" by maximizing distance to pacman.
            best = candidates[0]
            best_dist = -1
            for d in candidates:
                nxt = ghost.pos.moved(d)
                dist = manhattan(nxt, state.pacman.pos)
                if dist > best_dist:
                    best_dist = dist
                    best = d
            return best

        if self.mode == GhostMode.EATEN:
            target = ghost.home_pos
        elif self.mode == GhostMode.SCATTER:
            target = state.level.scatter_targets.get(self.ghost_id, state.pacman.pos)
        else:
            target = self.strategy.get_target(state, self.ghost_id)

        # Choose direction minimizing distance to target.
        best = candidates[0]
        best_dist = 10**9
        for d in candidates:
            nxt = ghost.pos.moved(d)
            dist = manhattan(nxt, target)
            if dist < best_dist:
                best_dist = dist
                best = d
        return best

