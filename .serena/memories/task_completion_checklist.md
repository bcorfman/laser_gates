# Task Completion Checklist

After completing any development task, ensure:

## Code Quality
- [ ] Code follows dependency injection patterns
- [ ] No runtime type checking (isinstance, hasattr, getattr)
- [ ] Velocity values use "pixels per frame" semantics
- [ ] Functions accept dependencies through constructors

## Testing
- [ ] Run full test suite: `uv run python -m pytest`
- [ ] Tests pass for modified components
- [ ] New features have corresponding tests
- [ ] Coverage maintained or improved

## Code Standards
- [ ] Format code: `ruff format .`
- [ ] Fix linting issues: `ruff check . --fix`
- [ ] No remaining linting errors
- [ ] Type hints added for public APIs

## Documentation
- [ ] Update docstrings for new/modified functions
- [ ] Follow Google docstring style
- [ ] Include usage examples where appropriate
- [ ] Update README or docs if API changes

## Integration
- [ ] No breaking changes to public API (unless intended)
- [ ] Backward compatibility maintained
- [ ] Changes follow project architecture (see docs/prd.md)
- [ ] Integration tests verify end-to-end functionality