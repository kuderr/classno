# Classno Bug Fix Plan

## Overview
This document outlines a systematic approach to fixing the critical bugs and issues identified in the classno library. The plan is organized by priority and includes implementation details, testing requirements, and risk assessments.

## Priority Classification

- **P0 (Critical)**: Breaks core functionality, must fix immediately
- **P1 (High)**: Significant impact, fix in current sprint
- **P2 (Medium)**: Quality issues, fix in next sprint
- **P3 (Low)**: Polish items, fix when time permits

---

## Phase 1: Critical Bug Fixes (P0)

### 1.1 Fix Equality Comparison Bug
**Target:** Bug #1 - `_dunders.py:55`
**Timeline:** 1 day
**Risk Level:** Low (simple fix, high impact)

**Implementation Steps:**
1. Change `other_key = getattr(self, key)()` to `other_key = getattr(other, key)()`
2. Review all comparison methods (`__eq__`, `__lt__`, `__le__`, `__gt__`, `__ge__`)
3. Ensure consistency across all comparison operations

**Files to Modify:**
- `classno/_dunders.py`

**Testing Requirements:**
- Add comprehensive equality tests for all comparison operators
- Test with custom `__eq_keys__` and `__order_keys__`
- Test inheritance scenarios
- Test edge cases (different types, None values)

**Validation:**
```python
class TestEq(Classno):
    __features__ = Features.EQ
    value: int

obj1 = TestEq(value=1)
obj2 = TestEq(value=2)
assert obj1 != obj2  # Should be False, not True
```

### 1.2 Fix Optional Type Validation
**Target:** Bug #2 - `_validation.py` Union handling
**Timeline:** 2-3 days
**Risk Level:** Medium (complex type system changes)

**Root Cause Analysis:**
The issue is in the Union type validation logic. When validating `Optional[T]` (which is `Union[T, None]`), the validator tries each type in the union but doesn't properly handle the `None` case.

**Implementation Steps:**
1. **Immediate Fix:** Add special handling for `Optional` types
2. **Proper Fix:** Rewrite Union validation logic

**Option A - Quick Fix:**
```python
def validate_value_hint(value, hint):
    # Special case for Optional types
    if (hasattr(hint, '__origin__') and hint.__origin__ is Union and
        type(None) in hint.__args__ and value is None):
        return  # None is valid for Optional types
    
    # Continue with existing logic...
```

**Option B - Proper Fix:**
```python
def validate_union_type(value, hint):
    """Properly validate Union types including Optional."""
    union_args = t.get_args(hint)
    
    # Check if value matches any type in the union
    for arg_type in union_args:
        try:
            if arg_type is type(None) and value is None:
                return  # Valid None for Optional
            elif arg_type is not type(None):
                validate_value_hint(value, arg_type)
                return  # Found valid type
        except TypeError:
            continue  # Try next type in union
    
    raise TypeError(f"Value {value} doesn't match any type in {hint}")
```

**Files to Modify:**
- `classno/_validation.py`

**Testing Requirements:**
- Test `Optional[str] = None`
- Test `Optional[int] = 42`
- Test `Union[str, int]` with both types
- Test nested Optional types
- Test complex unions like `Union[str, int, None]`

### 1.3 Add Missing Type Handlers
**Target:** Bug #3 - Missing validation/casting handlers
**Timeline:** 2 days
**Risk Level:** Low (additive changes)

**Implementation Steps:**
1. **Identify Missing Types:**
   - `frozenset`
   - `collections.deque`
   - `collections.defaultdict`
   - `collections.OrderedDict`
   - `collections.Counter`

2. **Add Validation Handlers:**
```python
def validate_frozenset(value, hint):
    tp, *_ = t.get_args(hint)
    for el in value:
        validate_value_hint(el, tp)

def validate_deque(value, hint):
    tp, *_ = t.get_args(hint)
    for el in value:
        validate_value_hint(el, tp)

VALIDATION_ORIGIN_HANDLER.update({
    frozenset: validate_frozenset,
    collections.deque: validate_deque,
    collections.defaultdict: validate_dict,  # Reuse dict handler
    collections.OrderedDict: validate_dict,  # Reuse dict handler
    collections.Counter: validate_dict,      # Reuse dict handler
})
```

3. **Add Casting Handlers:**
```python
def cast_frozenset(value, hint):
    tp, *_ = t.get_args(hint)
    new_set = set()
    for el in value:
        new_set.add(cast_value(el, tp))
    return frozenset(new_set)

CASTING_ORIGIN_HANDLER.update({
    frozenset: cast_frozenset,
    # ... other handlers
})
```

4. **Add Fallback Handler:**
```python
def get_validation_handler(origin):
    """Get validation handler with fallback logic."""
    if origin in VALIDATION_ORIGIN_HANDLER:
        return VALIDATION_ORIGIN_HANDLER[origin]
    
    # Fallback for collection-like types
    if hasattr(origin, '__iter__') and not isinstance(origin, (str, bytes)):
        return validate_collection
    
    raise KeyError(f"No validation handler for {origin}")
```

**Files to Modify:**
- `classno/_validation.py`
- `classno/_casting.py`

**Testing Requirements:**
- Test all new collection types with validation
- Test autocasting with new types
- Test edge cases and nested structures

---

## Phase 2: High Priority Fixes (P1)

### 2.1 Fix Shared Mutable Defaults
**Target:** Bug #4 - Shared mutable default values
**Timeline:** 2 days
**Risk Level:** Medium (behavioral change)

**Implementation Options:**

**Option A - Deep Copy Approach:**
```python
def init_obj(self, *args, **kwargs):
    import copy
    
    for field in self.__fields__.values():
        if field.name in kwargs:
            object.__setattr__(self, field.name, kwargs[field.name])
        elif field.default is not c.MISSING:
            # Deep copy mutable defaults
            default_value = copy.deepcopy(field.default)
            object.__setattr__(self, field.name, default_value)
        elif field.default_factory is not c.MISSING:
            object.__setattr__(self, field.name, field.default_factory())
        else:
            missing_fields.append(field.name)
```

**Option B - Validation Approach (Recommended):**
```python
def validate_field_default(field):
    """Validate that mutable objects use default_factory."""
    if field.default is not c.MISSING:
        # Check if default is mutable
        mutable_types = (list, dict, set)
        if isinstance(field.default, mutable_types):
            raise ValueError(
                f"Field '{field.name}' has mutable default {type(field.default)}. "
                f"Use default_factory=lambda: {field.default!r} instead."
            )
```

**Files to Modify:**
- `classno/_hooks.py`
- `classno/_fields.py` (add validation)

**Testing Requirements:**
- Test that mutable defaults are independent between instances
- Test that warnings/errors are raised for dangerous patterns
- Test performance impact of deep copying

### 2.2 Fix Casting Return Issues
**Target:** Bug #5 - Implicit None returns
**Timeline:** 1 day
**Risk Level:** Low

**Implementation:**
```python
def cast_value(value, hint):
    origin = t.get_origin(hint)

    # Unions: str | None, int | float, etc.
    if isinstance(hint, types.UnionType):
        for sub_hint in t.get_args(hint):
            with contextlib.suppress(TypeError):
                return cast_value(value, sub_hint)
        raise TypeError(f"Cannot cast {value} to any type in {hint}")

    # Simple type: int, bool, str, CustomClass, etc.
    if not origin:
        if isinstance(value, hint):
            return value
        return hint(value)  # Attempt casting

    if origin:
        if not isinstance(value, origin):
            raise TypeError(f"Cannot cast {type(value)} to {origin}")
        return CASTING_ORIGIN_HANDLER[origin](value, hint)
    
    # This should never be reached, but explicit is better than implicit
    raise TypeError(f"Unable to cast {value} of type {type(value)} to {hint}")
```

**Files to Modify:**
- `classno/_casting.py`

### 2.3 Comprehensive Test Suite Development
**Timeline:** 3-4 days
**Risk Level:** Low

**Test Categories:**
1. **Unit Tests:** Individual function testing
2. **Integration Tests:** Feature interaction testing  
3. **Edge Case Tests:** Boundary condition testing
4. **Performance Tests:** Large object/collection testing
5. **Regression Tests:** Prevent bug reintroduction

**Test Structure:**
```
tests/
├── unit/
│   ├── test_validation.py
│   ├── test_casting.py
│   ├── test_comparison.py
│   └── test_fields.py
├── integration/
│   ├── test_feature_combinations.py
│   └── test_inheritance.py
├── edge_cases/
│   ├── test_optional_types.py
│   ├── test_union_types.py
│   └── test_collection_types.py
└── regression/
    └── test_bug_fixes.py
```

---

## Phase 3: Medium Priority Fixes (P2)

### 3.1 Standardize Error Messages
**Timeline:** 1-2 days
**Risk Level:** Low

**Implementation:**
Create a centralized error formatting system:

```python
# classno/_errors.py
class ErrorFormatter:
    @staticmethod
    def validation_error(field_name, expected_type, actual_value, actual_type):
        return (f"For field '{field_name}', expected {expected_type} "
                f"but got {actual_value!r} of type {actual_type}")
    
    @staticmethod 
    def casting_error(field_name, value, value_type, target_type):
        return (f"For field '{field_name}', failed to cast {value!r} "
                f"of type {value_type} to {target_type}")
```

**Files to Modify:**
- `classno/_validation.py`
- `classno/_setattrs.py`
- `classno/_casting.py`

### 3.2 Remove Unnecessary Return Values
**Timeline:** 0.5 days
**Risk Level:** Low

**Implementation:**
```python
def setattr_processor(self, name: str, value: t.Any) -> None:
    # ... processing logic ...
    object.__setattr__(self, name, value)  # Remove 'return'
```

**Files to Modify:**
- `classno/_setattrs.py`

### 3.3 Address TODO Comments
**Timeline:** 1 day
**Risk Level:** Medium

**Review each TODO:**
1. `# TODO: move somewhere` - Evaluate if function placement is correct
2. `# TODO: dont override all of this if set by user` - Implement user override detection
3. `# TODO: should this two work together?` - Document feature interaction behavior

---

## Phase 4: Low Priority Polish (P3)

### 4.1 Fix Typos and Documentation
**Timeline:** 0.5 days
- Rename `copiyng.py` to `copying.py`
- Add docstrings to public functions
- Improve type annotations

### 4.2 Performance Optimizations
**Timeline:** 1-2 days
- Cache `getattr` results in comparison functions
- Optimize field access patterns
- Profile and optimize hot paths

---

## Implementation Timeline

### Week 1: Critical Fixes
- **Day 1:** Fix equality comparison bug
- **Day 2-3:** Fix Optional type validation
- **Day 4-5:** Add missing type handlers

### Week 2: High Priority & Testing
- **Day 1-2:** Fix mutable defaults issue
- **Day 3:** Fix casting return issues  
- **Day 4-5:** Develop comprehensive test suite

### Week 3: Medium Priority
- **Day 1-2:** Standardize error messages
- **Day 3:** Address TODO comments and cleanup
- **Day 4-5:** Code review and documentation

### Week 4: Polish & Release
- **Day 1:** Performance optimizations
- **Day 2:** Final testing and validation
- **Day 3-4:** Documentation updates
- **Day 5:** Release preparation

---

## Risk Mitigation

### High-Risk Changes
1. **Optional type validation:** Extensive testing required
2. **Mutable defaults:** May break existing code that relies on shared state

### Mitigation Strategies
1. **Feature flags:** Allow gradual rollout of fixes
2. **Deprecation warnings:** Warn before breaking changes
3. **Comprehensive testing:** Prevent regression
4. **Documentation:** Clear migration guides

### Rollback Plan
- Maintain current version as fallback
- Use git branches for each major fix
- Automated testing before merge

---

## Success Criteria

### Phase 1 Success
- [ ] All equality comparisons work correctly
- [ ] Optional types validate properly with None values
- [ ] No KeyError crashes on standard collection types
- [ ] All existing tests pass

### Phase 2 Success  
- [ ] No shared mutable default issues
- [ ] Robust autocasting without None returns
- [ ] Comprehensive test coverage (>95%)
- [ ] Performance regression tests pass

### Final Success
- [ ] All identified bugs fixed
- [ ] Test coverage >98%
- [ ] No breaking changes to public API
- [ ] Performance maintained or improved
- [ ] Documentation complete and accurate

---

## Notes

### Breaking Changes
The following fixes may introduce breaking changes:
1. **Mutable defaults validation** - Code using `field: list = []` will need to change
2. **Stricter type validation** - Previously accepted invalid types may now raise errors

### Backward Compatibility
Where possible, maintain backward compatibility through:
- Deprecation warnings instead of immediate errors
- Feature flags for new behavior
- Clear migration documentation