from __future__ import annotations

from pacman.app.use_cases import GameEngine
from pacman.domain.ghost_ai import BlinkyStrategy, PinkyStrategy
from pacman.domain.model import Direction


def test_blinky_targets_pacman_tile() -> None:
    e = GameEngine()
    state = e._state
    strat = BlinkyStrategy()
    assert strat.get_target(state, "blinky") == state.pacman.pos


def test_pinky_targets_ahead_of_pacman() -> None:
    e = GameEngine()
    state = e._state
    state.pacman.direction = Direction.RIGHT
    strat = PinkyStrategy(ahead=4)

    t = strat.get_target(state, "pinky")
    assert t.x == state.pacman.pos.x + 4
    assert t.y == state.pacman.pos.y

