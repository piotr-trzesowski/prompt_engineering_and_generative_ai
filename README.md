# Neon Pac (pygame + Clean Architecture)

Minimal Pac-Man-like game in Python 3 using pygame, Clean Architecture (domain/app/adapters/framework), Strategy pattern for ghost targeting, and a small ghost-mode state machine.

## Run

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -U pip
python3 -m pip install -r requirements.txt

python3 -m pacman.main
```

Controls: Arrow keys / WASD to turn, `R` to restart, `Esc` to quit.

## Architecture boundaries (quick)

- `pacman/domain/*`: pure rules + models + ghost AI (no pygame imports).
- `pacman/app/*`: use-cases/orchestration over the domain (no pygame imports).
- `pacman/adapters/*`: translates pygame input + rendering to/from domain snapshots.
- `pacman/framework/*`: pygame initialization + fixed-timestep loop.

