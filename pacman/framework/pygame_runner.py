from __future__ import annotations

import pygame

from pacman.adapters.pygame_input import command_from_events
from pacman.adapters.pygame_render import PygameRenderer
from pacman.app.use_cases import GameEngine


def run() -> None:
    pygame.init()
    pygame.display.set_caption("Neon Pac")

    engine = GameEngine(tile_size=24)
    snap = engine.snapshot()
    screen = pygame.display.set_mode((snap.width * engine.tile_size, snap.height * engine.tile_size))
    renderer = PygameRenderer(screen, engine.tile_size)

    clock = pygame.time.Clock()
    fixed = 1.0 / 60.0
    acc = 0.0

    running = True
    while running:
        frame_dt = clock.tick(60) / 1000.0
        if frame_dt > 0.25:
            frame_dt = 0.25
        acc += frame_dt

        events = pygame.event.get()
        for e in events:
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                running = False
            elif e.type == pygame.KEYDOWN and e.key == pygame.K_r:
                engine.reset_level()

        cmd = command_from_events(events)

        while acc >= fixed:
            engine.step_fixed(fixed, cmd)
            acc -= fixed

        renderer.draw(engine.snapshot())
        pygame.display.flip()

    pygame.quit()

