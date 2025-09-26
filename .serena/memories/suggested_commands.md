# Essential Commands for ArcadeActions Development

## Python Execution (CRITICAL)
```bash
# ALWAYS use uv run python instead of python directly
uv run python script.py
uv run python -m pytest
```

## Testing
```bash
# Run all tests
uv run python -m pytest

# Run with coverage
uv run python -m pytest --cov=actions

# Run specific test files
uv run python -m pytest tests/test_formation.py

# Run with markers
uv run python -m pytest -m unit
uv run python -m pytest -m system
```

## Code Quality
```bash
# Format and lint (automatic fixes)
ruff format .
ruff check . --fix

# Check without fixing
ruff check .
```

## Package Management
```bash
# Install dependencies
uv sync

# Add new dependency
uv add package-name

# Add dev dependency
uv add --dev package-name

# Update dependencies
uv lock --upgrade
```

## Build and Distribution
```bash
# Build package
uv run python -m build

# Install in development mode
uv pip install -e .
```

## Development Workflow
1. Make changes
2. Run tests: `uv run python -m pytest`
3. Format/lint: `ruff format . && ruff check . --fix`
4. Commit changes