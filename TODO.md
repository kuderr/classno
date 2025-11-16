# TODO - Future Enhancements

This document tracks planned improvements and enhancements for the Classno library. Items are organized by priority and category.

## High Priority

### Performance Optimizations

- [ ] **Add optional validation depth limits**

  - Add `max_depth` parameter to validation functions to prevent stack overflow on deeply nested structures
  - Default to reasonable limit (e.g., 100 levels) with option to disable
  - Track recursion depth during validation and casting

  ```python
  def validate_value_hint(value, hint, max_depth=100):
      if max_depth <= 0:
          raise RecursionError("Validation depth limit exceeded")
      # ... validation logic with max_depth - 1 for nested calls
  ```

- [ ] **Cache type handlers for frequently validated types**

  - Implement LRU cache for `get_origin()` and `get_args()` results
  - Cache handler lookups to avoid repeated dictionary access
  - Profile hot paths to identify optimization opportunities

- [ ] **Optimize comparison key access**
  - Cache `__eq_keys__`, `__hash_keys__`, `__order_keys__` lookups in comparison methods
  - Consider caching key tuples at instance level for frozen objects

### Testing & Quality

- [ ] **Add comprehensive benchmark suite**

  - Performance regression tests for validation, casting, and comparison
  - Memory usage benchmarks for slots vs non-slots classes
  - Benchmarks for deeply nested structures
  - Track performance across releases

- [ ] **Add type stubs (.pyi files)**

  - Improve IDE autocomplete and type checking
  - Better integration with mypy and other type checkers
  - Ensure all public APIs have proper type annotations

- [ ] **Performance profiling for large objects**
  - Profile validation/casting performance with large collections (10k+ items)
  - Identify and optimize bottlenecks
  - Consider lazy validation options for performance-critical paths

## Medium Priority

### Features & Functionality

- [ ] **Add strict/lossless autocasting mode**

  - Alternative to `LOSSY_AUTOCAST` that only allows safe conversions
  - Reject lossy conversions (e.g., float → int, str → bool)
  - New feature flag: `Features.STRICT_AUTOCAST`

  ```python
  class StrictModel(Classno):
      __features__ = Features.STRICT_AUTOCAST
      count: int

  # Should work: StrictModel(count=42)
  # Should fail: StrictModel(count=42.5)  # Lossy conversion
  ```

- [ ] **Field-level feature configuration**

  - Allow features to be specified per-field, not just class-level
  - Use field metadata to enable/disable features for specific fields

  ```python
  class MixedModel(Classno):
      validated_field: int = field(metadata={"features": Features.VALIDATION})
      unvalidated_field: str
  ```

- [ ] **Custom validation callbacks on fields**

  - Allow users to specify custom validators per field

  ```python
  def positive_validator(value):
      if value <= 0:
          raise ValueError("Must be positive")

  class Model(Classno):
      age: int = field(metadata={"validator": positive_validator})
  ```

- [ ] **Custom casting callbacks on fields**

  - Allow users to specify custom type converters per field

  ```python
  def parse_date(value):
      return datetime.strptime(value, "%Y-%m-%d")

  class Event(Classno):
      date: datetime = field(metadata={"caster": parse_date})
  ```

- [ ] **Cached/computed properties for immutable objects**

  - Automatically cache computed properties on frozen/immutable objects
  - Use `@cached_property` or similar for performance

  ```python
  class DataModel(Classno):
      __features__ = Features.IMMUTABLE
      items: list[int]

      @cached_property
      def total(self):
          return sum(self.items)  # Computed once, cached forever
  ```

### Documentation & Developer Experience

- [ ] **Add telemetry/logging for debugging**

  - Optional debug mode that logs validation and casting operations
  - Help users understand why validation fails
  - Configuration via environment variable or feature flag

- [ ] **Improve error messages for complex types**

  - Better error messages for nested Optional/Union types
  - Show the path to the failing field in nested structures
  - Example: "Validation error at path 'user.address.city': expected str, got int"

- [ ] **Add JSON schema generation**

  - Generate JSON Schema from Classno class definitions
  - Useful for API documentation and validation

  ```python
  schema = UserModel.to_json_schema()
  # {"type": "object", "properties": {...}}
  ```

- [ ] **Add dataclass compatibility mode**
  - Provide `@dataclass`-like decorator for easier migration
  - Drop-in replacement for existing dataclasses
  ```python
  @classno(frozen=True, validation=True)
  class User:
      name: str
      age: int
  ```

## Low Priority

### Quality of Life Improvements

- [ ] **Better repr recursion handling**

  - Currently mentioned as potential issue in original TODO
  - Implement cycle detection in `__repr__` for circular references
  - Gracefully handle self-referential structures

- [ ] **Fix validation when setting fields post-init**

  - Issue mentioned: "validation fail if set field"
  - Ensure validation runs on all field assignments when `VALIDATION` is enabled
  - Consider making this configurable (validate on init only vs always)

- [ ] **Add `from_dict` class method**

  - Complement to existing `as_dict()` instance method
  - Create instances from dictionaries easily

  ```python
  data = {"name": "John", "age": 30}
  user = User.from_dict(data)
  ```

- [ ] **Add `replace()` method for frozen objects**

  - Similar to dataclasses, create new instance with changed fields

  ```python
  user = User(name="John", age=30)
  updated = user.replace(age=31)  # New instance
  ```

- [ ] **Support for generic classes**

  - Allow Classno classes to be generic

  ```python
  from typing import Generic, TypeVar

  T = TypeVar('T')

  class Container(Classno, Generic[T]):
      value: T
  ```

### Ecosystem & Integrations

- [ ] **Pydantic interoperability**

  - Provide conversion utilities between Classno and Pydantic models
  - Learn from Pydantic's validator patterns

- [ ] **SQLAlchemy integration**

  - Utilities to convert Classno models to/from SQLAlchemy models
  - Consider ORM-like patterns

- [ ] **FastAPI integration examples**
  - Example code for using Classno with FastAPI
  - Request/response model examples

## Research & Investigation

- [ ] **Investigate Protocol support**

  - How Classno classes work with typing.Protocol
  - Ensure structural subtyping works as expected

- [ ] **Investigate metaclass conflicts**

  - Test compatibility with other metaclasses
  - Document known conflicts and workarounds

- [ ] **Research pattern matching support (Python 3.10+)**
  - Ensure Classno classes work well with structural pattern matching
  - Add examples if needed

## Completed Items

Items moved from the original TODO.md that are now resolved:

- [x] ~~Strict/lossless autocasting~~ - Marked for future consideration
- [x] ~~Features on fields~~ - Marked for future consideration
- [x] ~~Cached properties if immutable~~ - Marked for future consideration
- [x] ~~Validate callback on fields~~ - Marked for future consideration
- [x] ~~Cast callback on fields~~ - Marked for future consideration
- [x] ~~Validation fail if set field~~ - Needs investigation
- [x] ~~Repr recursion problem~~ - Needs investigation

---

## Notes

### Priority Levels

- **High Priority**: Should be addressed in the next major release
- **Medium Priority**: Nice-to-have features for future releases
- **Low Priority**: Quality of life improvements, no rush

### Contributing

If you're interested in working on any of these items:

1. Comment on the related GitHub issue (or create one)
2. Discuss the approach with maintainers
3. Submit a PR with tests and documentation
4. Update this TODO with your progress

### Performance Goals

- Maintain <1ms validation time for simple objects
- Support 10k+ item collections without significant slowdown
- Keep memory overhead minimal (slots should reduce by 40%+)
- Zero performance regression on non-validated classes
