# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Classno is a lightweight Python library for data modeling, schema definition, and validation. It provides a clean way to define data classes with type validation, immutability, private fields, and automatic type casting.

## Development Commands

This project uses **Poetry** for dependency management and **poethepoet** (poe) for task automation.

### Setup
```bash
poetry install
```

### Testing
```bash
# Run all tests with verbose output
poe tests

# Run specific test categories
poe test-unit          # Unit tests (fast, no slow tests)
poe test-integration   # Integration tests
poe test-edge-cases    # Edge case tests
poe test-regression    # Regression tests

# Run all tests with coverage
poe test-all           # Includes HTML coverage report

# Run fast tests only (skip slow tests, fail fast)
poe test-fast

# Generate coverage report with minimum 90% requirement
poe coverage-report

# Run a single test file
poetry run pytest tests/test_working_features.py -v

# Run a specific test
poetry run pytest tests/test_working_features.py::TestWorkingFeatures::test_validation_feature -v
```

### Linting and Formatting
```bash
# Check for linting issues (no fixes)
poe lint

# Auto-fix and format code
poe pretty
```

### Code Quality Tools
- **Ruff**: Linting and formatting (configured in ruff.toml)
- **pytest**: Testing framework with coverage
- **toml-sort**: TOML file formatting

## Architecture

### Core Components

**Metaclass System** (`classno/core.py`):
- `MetaClassno`: Metaclass that drives the entire feature system
- `Classno`: Base class for all data models
- `_prepare_slots_for_class()`: Handles slots configuration during class creation
- Flow: Class creation → `__new__` (slots prep) → field setup → feature processing → instance creation → `__init__` → feature application

**Hook System** (`classno/_hooks.py`):
- `init_obj()`: Initializes object fields from kwargs, defaults, and factories
- `set_fields()`: Collects field annotations from MRO and creates Field objects
- `process_cls_features()`: Applies class-level feature handlers
- `process_obj_features()`: Applies object-level feature handlers

**Field System** (`classno/_fields.py`):
- `Field`: Stores field metadata (name, type hint, default, factory, metadata)
- `field()`: Factory function for creating Field objects
- Validates mutable defaults (list, dict, set) and requires default_factory

**Feature System** (`classno/constants.py` + `classno/_feature_handlers.py`):
- Features are flags that can be combined with `|` operator
- Handlers split between class-level and object-level processing
- Feature combinations: `Features.IMMUTABLE = DEFAULT | HASH | SLOTS | FROZEN`

**Attribute Access** (`classno/_setattrs.py`, `_getattrs.py`, `_delattrs.py`):
- Custom `__setattr__` logic handles FROZEN, PRIVATE, VALIDATION, LOSSY_AUTOCAST
- Private feature: Write with `_name`, read with `name` (read-only public access)

**Validation System** (`classno/_validation.py`):
- Type checking for primitives, collections, Optional, Union types
- Supports both `typing.Union` and `types.UnionType` (Python 3.10+ union syntax)
- Extended collection support: `frozenset`, `deque`, `defaultdict`, `OrderedDict`, `Counter`
- ForwardRef handling for circular/self-referential types
- Fallback handler for unknown iterable types
- Recursive validation for nested Classno objects

**Type Casting** (`classno/_casting.py`):
- LOSSY_AUTOCAST feature: Automatic type conversion (str→int, float→int, etc.)
- Handles primitives, collections, and Union types
- Special handling for Optional types (Union with None)
- Dict casting includes both keys AND values
- Boolean string parsing ("true", "false", "yes", "no")
- Extended collection support matching validation system

**Error Handling** (`classno/_errors.py`):
- Centralized error message formatting via `ErrorFormatter` class
- Consistent, actionable error messages across all modules
- Helpful suggestions in error messages (e.g., mutable defaults)

### Test Organization

**Test Structure**:
- `tests/unit/`: Focused unit tests for specific functionality
- `tests/integration/`: Cross-feature integration tests
- `tests/edge_cases/`: Edge case and boundary testing
- `tests/regression/`: Tests for previously fixed bugs
- Root-level test files: Comprehensive scenario testing

**Key Test Files**:
- `test_working_features.py`: Canonical reference for all working features
- `test_comprehensive_scenarios.py`: Real-world usage patterns
- `tests/README_TESTS.md`: Detailed test documentation

### Important Implementation Details

1. **Slots and Inheritance**: When slots are enabled, the metaclass moves field defaults to `_field_defaults` to avoid conflicts with `__slots__`

2. **Field Resolution**: Fields are collected from entire MRO using `get_type_hints()` with fallback to raw annotations for forward references

3. **Feature Processing Order**:
   - Class creation: `__new__` → slots prep → field setup → class features
   - Instance creation: `__init__` → object features (LOSSY_AUTOCAST → VALIDATION) → `__post__init__`
   - **Critical**: LOSSY_AUTOCAST always runs before VALIDATION to ensure casting happens first

4. **Comparison Keys**: Custom `__eq_keys__`, `__hash_keys__`, `__order_keys__` use **tuples** (not sets/lists) to preserve order and immutability. Keys are auto-generated if not explicitly defined, with smart inheritance detection via `_autogenerated` markers.

5. **Mutable Defaults**: Library explicitly prevents mutable defaults (list, dict, set, bytearray) and requires `default_factory` to avoid shared state. Validation happens at class definition time.

6. **Union/Optional Handling**: Both `typing.Union` and `types.UnionType` (Python 3.10+ `X | Y` syntax) are fully supported. Optional types are handled specially - `None` values pass validation immediately if `None` is in the union.

7. **Dict Casting**: When casting dicts, both keys AND values are cast to their target types (not just values)

8. **Error Messages**: All error messages use centralized `ErrorFormatter` for consistency and helpful suggestions

## Features Reference

Available feature flags in `Features` enum:
- `EQ`: Equality comparison
- `ORDER`: Ordering operations (`<`, `>`, etc.)
- `HASH`: Make instances hashable
- `SLOTS`: Use `__slots__` for memory optimization
- `FROZEN`: Immutable after creation
- `PRIVATE`: Private field access patterns
- `VALIDATION`: Runtime type validation
- `LOSSY_AUTOCAST`: Automatic type casting
- `DEFAULT`: `EQ | REPR | ORDER`
- `IMMUTABLE`: `DEFAULT | HASH | SLOTS | FROZEN`

## Best Practices

1. **Always run tests after changes**: Use `poe test-fast` for quick validation
2. **Enable validation for type safety**: Use `Features.VALIDATION` when type correctness is critical
3. **Use slots for performance**: Enable `Features.SLOTS` for memory-constrained scenarios
4. **Prefer explicit defaults**: Avoid `Optional[T] = None`, use explicit defaults instead
5. **Use factory for mutable defaults**: Always use `field(default_factory=list)` not `field(default=[])`
6. **Test feature combinations**: Some features interact in non-obvious ways
7. **Check test documentation**: See `tests/README_TESTS.md` for known limitations

## Common Pitfalls

1. **Slots + Inheritance**: Child classes must also use slots or explicitly define `__dict__`
2. **Comparison Keys Must Be Tuples**: Use `__eq_keys__ = ("id", "name")` not `["id", "name"]` or `{"id", "name"}`
3. **Private Fields**: Write with `_field`, read-only access with `field`
4. **Frozen + Slots**: Must be used together for true immutability
5. **Mutable Defaults**: Never use `field: list = []`. Always use `field: list = field(default_factory=list)`
6. **Feature Order Matters**: When combining LOSSY_AUTOCAST and VALIDATION, casting happens first automatically

## Recent Changes & Fixes

The codebase has undergone significant improvements:

1. **Fixed critical comparison bug**: Equality/ordering comparisons now correctly compare two different objects (not self with self)
2. **Fixed Optional/Union validation**: Full support for `Optional[T]`, `Union[T1, T2]`, and Python 3.10+ `T1 | T2` syntax
3. **Extended collection support**: Added handlers for `frozenset`, `deque`, `defaultdict`, `OrderedDict`, `Counter`
4. **Fixed dict casting**: Both keys and values are now cast (previously only values)
5. **Mutable defaults prevention**: Now raises clear errors at class definition time with helpful suggestions
6. **Centralized error handling**: All error messages use `ErrorFormatter` for consistency
7. **Comparison keys are tuples**: Changed from sets to tuples for order preservation and immutability

See `tests/regression/test_bug_fixes.py` for regression tests covering all fixed bugs.
