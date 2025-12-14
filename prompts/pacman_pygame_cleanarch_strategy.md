---
name: pacman_pygame_cleanarch_strategy
version: 1.0
target_model: gpt-5.2
purpose: "Generate a minimal Pac-Man-like game in Python using Pygame, Clean Architecture, and Strategy pattern."
coding_style: "minimalistic, easy to read, clean"
notes:
  - "No external assets required; use procedural shapes for a cyberpunk look."
  - "Prefer dataclasses, type hints, small modules, no magic."
---

<SYSTEM>
You are an expert Python game developer.
Write minimalistic, readable, clean Python 3 code.
Priorities (in order):

1) Correctness and playability
2) Clean Architecture separation (domain/app/adapters/framework)
3) Strategy pattern for ghost targeting
4) Performance (smooth 60 FPS), simple and maintainable code
Avoid unnecessary abstractions and avoid overengineering.
</SYSTEM>

<USER>
Task: Create a Pac-Man-style game using Pygame.

Hard requirements:
- Framework: Pygame (pip install pygame)
- Architecture: Clean Architecture style layering:
  - domain/ : pure game rules, entities, components; MUST NOT import pygame
  - app/    : use-cases/systems coordinating domain; MUST NOT import pygame
  - adapters/ : translate between pygame and app/domain (input mapping, rendering mapping)
  - framework/ (or main.py): pygame loop, window setup, audio hooks (optional)
- Patterns:
  - Strategy pattern: ghost targeting behaviors must be swappable strategies
  - State machine: ghost modes (CHASE, SCATTER, FRIGHTENED, EATEN) at minimum
  - Command-like input buffering: store desired direction and apply when valid
- Minimal and clean code:
  - type hints everywhere
  - dataclasses where appropriate
  - clear naming, short functions, no deep nesting
  - no global state (except constants)
- Performance:
  - fixed timestep update (deterministic movement) + render loop
  - avoid per-frame heavy allocations
- Visual style:
  - Futuristic/cyberpunk vibe
  - Background: dark
  - Primary palette: neon blue + neon yellow accents
  - Ghost colors: pick cyberpunk-friendly variants (e.g., magenta/cyan/lime/orange), but keep readable
  - No external images required: draw with pygame primitives (rect/circle/lines)
- Gameplay:
  - Tile/grid-based maze
  - Pellets to collect; power pellet triggers frightened mode
  - Basic scoring, lives, and level reset on death
  - Ghosts leave a “home” area (simple implementation OK)
  - Tunnels on left/right edges (optional if simple)
- Deliverables:
  1) Project tree
  2) Full source code for all files
  3) How to run (commands)
  4) Short explanation of architecture boundaries (1 paragraph max)

Project layout (use exactly these names):
pacman/
  main.py
  domain/
    __init__.py
    model.py            # dataclasses: GameState, Entity, Grid, etc.
    rules.py            # collisions, scoring, pellet rules
    ghost_ai.py         # strategies + ghost state machine (NO pygame)
  app/
    __init__.py
    use_cases.py        # tick/update orchestration, mode timers
    commands.py         # input commands (TurnUp/Down/Left/Right)
  adapters/
    __init__.py
    pygame_input.py     # pygame -> commands
    pygame_render.py    # domain snapshot -> draw calls (pygame imports allowed here)
  framework/
    __init__.py
    pygame_runner.py    # game loop, fixed timestep, window init

Class names (use these):
- domain.model:
  - Direction (Enum)
  - GridPos (dataclass)
  - Entity (dataclass)
  - Pacman(Entity)
  - Ghost(Entity)
  - GameSnapshot (dataclass)   # immutable-ish view passed to renderer
  - Level (dataclass)          # grid + pellets
- domain.ghost_ai:
  - GhostMode (Enum)
  - TargetStrategy (Protocol)
  - BlinkyStrategy, PinkyStrategy, InkyStrategy, ClydeStrategy
  - GhostBrain (class)         # holds mode + strategy + decision logic
- app.use_cases:
  - GameEngine (class)         # update(dt), step_fixed(), reset_level()
- app.commands:
  - TurnCommand (Protocol or base class)
  - TurnUp/TurnDown/TurnLeft/TurnRight

Strict boundary rules:
- domain/* must not import pygame
- app/* must not import pygame
- only adapters/* and framework/* may import pygame

Output rules:
- Output code blocks per file, clearly labeled with file path.
- Do not omit files. Include __init__.py files.
- Do not include long essays.
- If you must simplify, simplify features, not architecture boundaries.
</USER>
