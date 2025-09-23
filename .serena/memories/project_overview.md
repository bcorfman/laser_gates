# ArcadeActions Project Overview

## Purpose
ArcadeActions is an extension library for Arcade 3.x Python library that provides a high-level, declarative action system for animating sprites with conditional actions. It's inspired by Cocos2D's action system but reimagined for Arcade's API.

## Tech Stack
- **Python**: 3.10+ (targeting 3.12)
- **Dependencies**: Arcade 3.x, Pyglet 2.1+, screeninfo, PySDL2
- **Build**: Hatchling (pyproject.toml based)
- **Testing**: Pytest with coverage
- **Linting/Formatting**: Ruff
- **Package Management**: UV (uses uv.lock, run with `uv run python`)

## Key Features
- Conditional actions (MoveUntil, RotateUntil, ScaleUntil, etc.)
- Composition functions (sequence, parallel, repeat)
- Formation functions for sprite arrangement
- Boundary handling and easing effects
- Helper functions for common patterns

## Project Structure
```
arcade_actions/
├── actions/           # Main library code
│   ├── base.py       # Core Action class and management
│   ├── conditional.py # Condition-based actions
│   ├── composite.py  # Sequential/parallel compositions
│   ├── formation.py  # Formation arrangement functions
│   ├── helpers.py    # Convenience wrappers
│   └── ...
├── tests/            # Test suite
├── docs/             # Documentation
├── examples/         # Demo applications
└── pyproject.toml    # Project configuration
```