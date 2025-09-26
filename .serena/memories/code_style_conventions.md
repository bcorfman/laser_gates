# Code Style and Conventions

## Code Style
- **Line length**: 120 characters
- **Quotes**: Double quotes for strings
- **Formatting**: Ruff (automatic fixes enabled)
- **Type hints**: Required for all public APIs
- **Docstrings**: Google style, code formatting enabled

## Naming Conventions
- **Functions**: snake_case
- **Classes**: PascalCase
- **Constants**: UPPER_CASE
- **Private**: Leading underscore

## Design Principles (CRITICAL)
1. **Dependency Injection**: Accept dependencies through constructors
2. **Interface Design**: Zero tolerance for runtime type checking (isinstance, hasattr, getattr)
3. **API Quality**: Pleasant developer experience, simplicity, library API compliance
4. **Velocity Semantics**: ALL velocity values use "pixels per frame at 60 FPS", NOT "pixels per second"

## Forbidden Patterns
- Runtime type checking with isinstance, hasattr, getattr
- Direct instantiation of dependencies inside methods (except constructors)
- Static method calls for mockable dependencies
- Circular dependencies

## Lint Rules (Ruff)
- pycodestyle (E), Pyflakes (F), pyupgrade (UP)
- flake8-bugbear (B), flake8-simplify (SIM), isort (I)
- Banned APIs for isinstance, hasattr, getattr with custom messages