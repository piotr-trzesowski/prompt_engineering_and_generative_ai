from __future__ import annotations

import math

import pygame

from pacman.domain.model import Direction, GameSnapshot, GridPos


NEON_BLUE = (0, 210, 255)
NEON_YELLOW = (255, 240, 60)
NEON_MAGENTA = (255, 60, 210)
NEON_CYAN = (60, 255, 240)
NEON_LIME = (100, 255, 120)
NEON_ORANGE = (255, 150, 60)
BG = (6, 6, 12)
GRID = (18, 18, 40)
TEXT = (210, 210, 230)

GHOST_COLORS = {
    "blinky": NEON_MAGENTA,
    "pinky": (255, 110, 220),
    "inky": NEON_CYAN,
    "clyde": NEON_ORANGE,
}


class PygameRenderer:
    def __init__(self, screen: pygame.Surface, tile_size: int) -> None:
        self._screen = screen
        self._tile = tile_size
        self._font = pygame.font.Font(None, 24)

    def draw(self, snap: GameSnapshot) -> None:
        self._screen.fill(BG)
        self._draw_grid(snap)
        self._draw_walls(snap)
        self._draw_pellets(snap)
        self._draw_entities(snap)
        self._draw_hud(snap)

    def _px_center(self, pos: GridPos) -> tuple[int, int]:
        return (
            pos.x * self._tile + self._tile // 2,
            pos.y * self._tile + self._tile // 2,
        )

    def _draw_grid(self, snap: GameSnapshot) -> None:
        w = snap.width * self._tile
        h = snap.height * self._tile
        for x in range(0, w, self._tile):
            pygame.draw.line(self._screen, GRID, (x, 0), (x, h), 1)
        for y in range(0, h, self._tile):
            pygame.draw.line(self._screen, GRID, (0, y), (w, y), 1)

    def _draw_walls(self, snap: GameSnapshot) -> None:
        for p in snap.walls:
            r = pygame.Rect(p.x * self._tile, p.y * self._tile, self._tile, self._tile)
            pygame.draw.rect(self._screen, (10, 10, 22), r)
            pygame.draw.rect(self._screen, NEON_BLUE, r, 2)

    def _draw_pellets(self, snap: GameSnapshot) -> None:
        for p in snap.pellets:
            cx, cy = self._px_center(p)
            pygame.draw.circle(self._screen, (190, 200, 220), (cx, cy), max(2, self._tile // 10))
        for p in snap.power_pellets:
            cx, cy = self._px_center(p)
            pygame.draw.circle(self._screen, NEON_YELLOW, (cx, cy), max(4, self._tile // 5), 0)
            pygame.draw.circle(self._screen, (20, 20, 40), (cx, cy), max(2, self._tile // 8), 0)

    def _draw_entities(self, snap: GameSnapshot) -> None:
        # Pac-Man
        px, py = self._px_center(snap.pacman_pos)
        r = self._tile // 2 - 2
        pygame.draw.circle(self._screen, NEON_YELLOW, (px, py), r)
        # mouth
        ang = {
            Direction.RIGHT: 0.0,
            Direction.LEFT: math.pi,
            Direction.UP: -math.pi / 2,
            Direction.DOWN: math.pi / 2,
            Direction.NONE: 0.0,
        }[snap.pacman_direction]
        mouth = 0.55
        pts = [
            (px, py),
            (px + int(math.cos(ang + mouth) * r), py + int(math.sin(ang + mouth) * r)),
            (px + int(math.cos(ang - mouth) * r), py + int(math.sin(ang - mouth) * r)),
        ]
        pygame.draw.polygon(self._screen, BG, pts)

        # Ghosts
        for g in snap.ghosts:
            cx, cy = self._px_center(g.pos)
            col = GHOST_COLORS.get(g.ghost_id, NEON_BLUE)
            if g.mode == "FRIGHTENED":
                col = (120, 160, 255)
            if g.mode == "EATEN":
                col = (120, 120, 140)
            body = pygame.Rect(cx - r, cy - r, 2 * r, 2 * r)
            pygame.draw.rect(self._screen, col, body, border_radius=r)
            pygame.draw.rect(self._screen, (0, 0, 0), body, 2, border_radius=r)
            eye_off = r // 3
            pygame.draw.circle(self._screen, (10, 10, 12), (cx - eye_off, cy - eye_off), max(2, r // 6))
            pygame.draw.circle(self._screen, (10, 10, 12), (cx + eye_off, cy - eye_off), max(2, r // 6))

    def _draw_hud(self, snap: GameSnapshot) -> None:
        msg = f"Score {snap.score}   Lives {snap.lives}   Mode {snap.mode}"
        if snap.frightened_left > 0:
            msg += f"   Fright {snap.frightened_left:0.1f}s"
        if snap.game_over:
            msg = "GAME OVER  - press R to restart"
        if snap.level_complete:
            msg = "LEVEL CLEAR - press R to restart"
        surf = self._font.render(msg, True, TEXT)
        self._screen.blit(surf, (8, 6))

