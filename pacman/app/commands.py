from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from pacman.domain.model import Direction


class TurnCommand(Protocol):
    def direction(self) -> Direction: ...


@dataclass(frozen=True, slots=True)
class TurnUp:
    def direction(self) -> Direction:
        return Direction.UP


@dataclass(frozen=True, slots=True)
class TurnDown:
    def direction(self) -> Direction:
        return Direction.DOWN


@dataclass(frozen=True, slots=True)
class TurnLeft:
    def direction(self) -> Direction:
        return Direction.LEFT


@dataclass(frozen=True, slots=True)
class TurnRight:
    def direction(self) -> Direction:
        return Direction.RIGHT

