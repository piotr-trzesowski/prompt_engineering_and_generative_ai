from __future__ import annotations

import pygame

from pacman.app.commands import TurnCommand, TurnDown, TurnLeft, TurnRight, TurnUp


def command_from_events(events: list[pygame.event.Event]) -> TurnCommand | None:
    cmd: TurnCommand | None = None
    for e in events:
        if e.type != pygame.KEYDOWN:
            continue
        if e.key in (pygame.K_UP, pygame.K_w):
            cmd = TurnUp()
        elif e.key in (pygame.K_DOWN, pygame.K_s):
            cmd = TurnDown()
        elif e.key in (pygame.K_LEFT, pygame.K_a):
            cmd = TurnLeft()
        elif e.key in (pygame.K_RIGHT, pygame.K_d):
            cmd = TurnRight()
    return cmd

