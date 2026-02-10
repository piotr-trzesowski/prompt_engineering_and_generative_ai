from __future__ import annotations

from dataclasses import dataclass

from pacman.app.commands import TurnCommand
from pacman.domain.ghost_ai import (
    BlinkyStrategy,
    ClydeStrategy,
    GhostBrain,
    GhostMode,
    InkyStrategy,
    PinkyStrategy,
)
from pacman.domain.model import (
    Direction,
    GameSnapshot,
    GameState,
    Ghost,
    GhostView,
    GridPos,
    Level,
    Pacman,
)
from pacman.domain.rules import GHOST_EATEN_SCORE, apply_pellet_rules, can_move, wrap_tunnel


TILE_SPEED_PACMAN = 8.0
TILE_SPEED_GHOST = 7.0
FRIGHTENED_SECS = 8.0


@dataclass(slots=True)
class GameEngine:
    tile_size: int = 24

    _state: GameState = None  # type: ignore[assignment]
    _brains: dict[str, GhostBrain] = None  # type: ignore[assignment]
    _move_acc_p: float = 0.0
    _move_acc_g: dict[str, float] = None  # type: ignore[assignment]
    _global_mode: GhostMode = GhostMode.SCATTER
    _mode_timer: float = 0.0
    _mode_index: int = 0
    _schedule: list[tuple[GhostMode, float]] = None  # type: ignore[assignment]
    _frightened_left: float = 0.0
    _release_order: list[str] = None  # type: ignore[assignment]
    _release_index: int = 0
    _release_timer: float = 0.0

    def __post_init__(self) -> None:
        self._state = self._new_game_state()
        self._brains = self._new_brains()
        self._move_acc_p = 0.0
        self._move_acc_g: dict[str, float] = {gid: 0.0 for gid in self._state.ghosts}
        self._global_mode = GhostMode.SCATTER
        self._mode_timer = 0.0
        self._mode_index = 0
        # scatter/chase schedule in seconds (simplified)
        self._schedule: list[tuple[GhostMode, float]] = [
            (GhostMode.SCATTER, 7.0),
            (GhostMode.CHASE, 20.0),
            (GhostMode.SCATTER, 7.0),
            (GhostMode.CHASE, 9999.0),
        ]
        self._frightened_left = 0.0
        self._release_order = ["blinky", "pinky", "inky", "clyde"]
        self._release_index = 0
        self._release_timer = 0.0

    def reset_level(self) -> None:
        self._state = self._new_game_state()
        self._brains = self._new_brains()
        self._move_acc_p = 0.0
        self._move_acc_g = {gid: 0.0 for gid in self._state.ghosts}
        self._global_mode = GhostMode.SCATTER
        self._mode_timer = 0.0
        self._mode_index = 0
        self._frightened_left = 0.0
        self._release_index = 0
        self._release_timer = 0.0

    def step_fixed(self, dt: float, cmd: TurnCommand | None) -> None:
        if self._state.game_over or self._state.level_complete:
            return

        if cmd is not None:
            self._state.pacman.desired_direction = cmd.direction()

        pellet_res = apply_pellet_rules(self._state)
        if pellet_res.power_eaten:
            self._frightened_left = FRIGHTENED_SECS

        self._update_modes(dt)
        self._update_pacman(dt)
        self._update_ghost_release(dt)
        self._update_ghosts(dt)
        self._resolve_collisions()

    def snapshot(self) -> GameSnapshot:
        ghosts = tuple(
            GhostView(ghost_id=g.ghost_id, pos=g.pos, mode=self._brains[g.ghost_id].mode.value)
            for g in self._state.ghosts.values()
        )
        return GameSnapshot(
            width=self._state.level.width,
            height=self._state.level.height,
            walls=self._state.level.walls,
            pellets=frozenset(self._state.level.pellets),
            power_pellets=frozenset(self._state.level.power_pellets),
            pacman_pos=self._state.pacman.pos,
            pacman_direction=self._state.pacman.direction,
            lives=self._state.lives,
            ghosts=ghosts,
            score=self._state.score,
            mode=self._global_mode.value,
            frightened_left=self._frightened_left,
            game_over=self._state.game_over,
            level_complete=self._state.level_complete,
        )

    def _new_brains(self) -> dict[str, GhostBrain]:
        return {
            "blinky": GhostBrain("blinky", BlinkyStrategy(), GhostMode.SCATTER),
            "pinky": GhostBrain("pinky", PinkyStrategy(), GhostMode.SCATTER),
            "inky": GhostBrain("inky", InkyStrategy(), GhostMode.SCATTER),
            "clyde": GhostBrain("clyde", ClydeStrategy(), GhostMode.SCATTER),
        }

    def _update_modes(self, dt: float) -> None:
        if self._frightened_left > 0.0:
            self._frightened_left = max(0.0, self._frightened_left - dt)

        if self._frightened_left <= 0.0:
            self._mode_timer += dt
            mode, duration = self._schedule[self._mode_index]
            self._global_mode = mode
            if self._mode_timer >= duration and self._mode_index < len(self._schedule) - 1:
                self._mode_index += 1
                self._mode_timer = 0.0

        for gid, brain in self._brains.items():
            if brain.mode == GhostMode.EATEN:
                continue
            if self._frightened_left > 0.0:
                brain.set_mode(GhostMode.FRIGHTENED)
            else:
                brain.set_mode(self._global_mode)

    def _update_pacman(self, dt: float) -> None:
        self._move_acc_p += dt * TILE_SPEED_PACMAN
        while self._move_acc_p >= 1.0:
            self._move_acc_p -= 1.0
            p = self._state.pacman

            if can_move(self._state.level, p.pos, p.desired_direction):
                p.direction = p.desired_direction

            if can_move(self._state.level, p.pos, p.direction):
                nxt = wrap_tunnel(self._state.level.width, p.pos.moved(p.direction))
                p.pos = nxt

            apply_pellet_rules(self._state)

    def _update_ghost_release(self, dt: float) -> None:
        # Keep ghosts in home until time passes; blinky released immediately.
        self._release_timer += dt
        if self._release_index >= len(self._release_order):
            return
        if self._release_index == 0:
            self._release_index = 1
            return
        if self._release_timer >= 4.0:
            self._release_timer = 0.0
            self._release_index += 1

    def _ghost_is_released(self, ghost_id: str) -> bool:
        if ghost_id not in self._release_order:
            return True
        idx = self._release_order.index(ghost_id)
        return idx < self._release_index

    def _update_ghosts(self, dt: float) -> None:
        for gid, ghost in self._state.ghosts.items():
            if not self._ghost_is_released(gid) and self._brains[gid].mode != GhostMode.EATEN:
                continue

            self._move_acc_g[gid] += dt * TILE_SPEED_GHOST
            while self._move_acc_g[gid] >= 1.0:
                self._move_acc_g[gid] -= 1.0

                valid_dirs: list[Direction] = []
                for d in (Direction.UP, Direction.LEFT, Direction.DOWN, Direction.RIGHT):
                    if can_move(self._state.level, ghost.pos, d):
                        valid_dirs.append(d)

                disallow_reverse = self._brains[gid].mode not in (GhostMode.FRIGHTENED, GhostMode.EATEN)
                chosen = self._brains[gid].choose_dir(self._state, ghost, valid_dirs, disallow_reverse)
                if chosen != Direction.NONE and can_move(self._state.level, ghost.pos, chosen):
                    ghost.direction = chosen
                    ghost.pos = wrap_tunnel(self._state.level.width, ghost.pos.moved(chosen))

                if self._brains[gid].mode == GhostMode.EATEN and ghost.pos == ghost.home_pos:
                    self._brains[gid].set_mode(self._global_mode if self._frightened_left <= 0 else GhostMode.FRIGHTENED)

    def _resolve_collisions(self) -> None:
        ppos = self._state.pacman.pos
        for gid, ghost in self._state.ghosts.items():
            if ghost.pos != ppos:
                continue

            brain = self._brains[gid]
            if brain.mode == GhostMode.FRIGHTENED:
                self._state.score += GHOST_EATEN_SCORE
                brain.set_mode(GhostMode.EATEN)
                ghost.pos = ghost.pos  # keep; will head home
            elif brain.mode != GhostMode.EATEN:
                self._state.lives -= 1
                if self._state.lives <= 0:
                    self._state.game_over = True
                    return
                self._reset_positions()
                return

    def _reset_positions(self) -> None:
        self._state.pacman.pos = self._state.level.pacman_spawn
        self._state.pacman.direction = Direction.LEFT
        self._state.pacman.desired_direction = Direction.LEFT
        for gid, ghost in self._state.ghosts.items():
            ghost.pos = ghost.spawn_pos
            ghost.direction = Direction.UP
            if self._brains[gid].mode != GhostMode.EATEN:
                self._brains[gid].set_mode(GhostMode.SCATTER)
        self._frightened_left = 0.0
        self._global_mode = GhostMode.SCATTER
        self._mode_timer = 0.0
        self._mode_index = 0
        self._release_index = 0
        self._release_timer = 0.0

    def _new_game_state(self) -> GameState:
        level = _make_level()
        pacman = Pacman(pos=level.pacman_spawn, direction=Direction.LEFT, desired_direction=Direction.LEFT, lives=3)
        ghosts = {
            gid: Ghost(ghost_id=gid, pos=spawn, direction=Direction.UP, spawn_pos=spawn, home_pos=level.ghost_home)
            for gid, spawn in level.ghost_spawns.items()
        }
        return GameState(
            level=level,
            pacman=pacman,
            ghosts=ghosts,
            score=0,
            lives=3,
            game_over=False,
            level_complete=False,
            frightened_left=0.0,
        )


def _make_level() -> Level:
    # Simple maze style: # wall, . pellet, o power pellet, P pacman, G ghost home marker.
    raw = [
        "#####################",
        "#o........#........o#",
        "#.###.###.#.###.###.#",
        "#...................#",
        "#.###.#.#####.#.###.#",
        "#.....#...#...#.....#",
        "#####.###.#.###.#####",
        "#####.#...G...#.#####",
        "#####.#.##.##.#.#####",
        "#.........#.........#",
        "#.###.###.#.###.###.#",
        "#o..#.....P.....#..o#",
        "###.#.#.#####.#.#.###",
        "#.....#...#...#.....#",
        "#.#########.#########",
        "#...................#",
        "#####################",
    ]

    height = len(raw)
    width = len(raw[0])

    walls: set[GridPos] = set()
    pellets: set[GridPos] = set()
    power: set[GridPos] = set()

    pac_spawn = GridPos(1, 1)
    ghost_home = GridPos(width // 2, height // 2)

    for y, row in enumerate(raw):
        if len(row) != width:
            raise ValueError("Level rows must be same width")
        for x, ch in enumerate(row):
            pos = GridPos(x, y)
            if ch == "#":
                walls.add(pos)
            elif ch == ".":
                pellets.add(pos)
            elif ch == "o":
                power.add(pos)
            elif ch == "P":
                pac_spawn = pos
            elif ch == "G":
                ghost_home = pos

    # Carve pellets out of walls/home/spawn area.
    pellets.discard(pac_spawn)
    power.discard(pac_spawn)

    ghost_spawns = {
        "blinky": ghost_home.moved(Direction.UP),
        "pinky": ghost_home,
        "inky": ghost_home.moved(Direction.LEFT),
        "clyde": ghost_home.moved(Direction.RIGHT),
    }

    scatter = {
        "blinky": GridPos(width - 2, 1),
        "pinky": GridPos(1, 1),
        "inky": GridPos(width - 2, height - 2),
        "clyde": GridPos(1, height - 2),
    }

    return Level(
        width=width,
        height=height,
        walls=frozenset(walls),
        pellets=pellets,
        power_pellets=power,
        pacman_spawn=pac_spawn,
        ghost_spawns=ghost_spawns,
        ghost_home=ghost_home,
        scatter_targets=scatter,
    )

