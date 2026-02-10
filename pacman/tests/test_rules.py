from __future__ import annotations

from pacman.app.use_cases import GameEngine
from pacman.domain.model import GridPos


def test_pellet_consumption_increases_score() -> None:
    e = GameEngine()
    s0 = e.snapshot()

    # Put pacman on a pellet tile (pick any existing pellet)
    pellet_pos = next(iter(s0.pellets))
    e._state.pacman.pos = pellet_pos  # domain-only test convenience

    score0 = e.snapshot().score
    e.step_fixed(1 / 60, None)
    s1 = e.snapshot()

    assert s1.score >= score0 + 10
    assert pellet_pos not in s1.pellets


def test_level_complete_when_no_pellets() -> None:
    e = GameEngine()
    e._state.level.pellets.clear()
    e._state.level.power_pellets.clear()

    e.step_fixed(1 / 60, None)
    assert e.snapshot().level_complete is True

