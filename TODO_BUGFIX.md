# Classno Bug Fix TODO List

## Phase 1: Critical Fixes (P0) - Week 1 ✅ COMPLETED

### 🔥 Day 1: Fix Equality Comparison Bug ✅ COMPLETED

- [x] **Code Changes**
  - [x] Fix `_dunders.py:55` - Changed `getattr(self, key)()` to `getattr(other, key)()`
  - [x] Reviewed all comparison methods (`__eq__`, `__lt__`, `__le__`, `__gt__`, `__ge__`)
  - [x] Ensured consistency across all comparison operations
- [x] **Testing**
  - [x] Created `tests/unit/test_comparison_fix.py` with 13 comprehensive tests
  - [x] Tested basic equality: `obj1 == obj2` with different values
  - [x] Tested inequality: `obj1 != obj2`
  - [x] Tested ordering: `obj1 < obj2`, `obj1 <= obj2`, `obj1 > obj2`, `obj1 >= obj2`
  - [x] Tested with custom `__eq_keys__` and `__order_keys__`
  - [x] Tested inheritance scenarios
  - [x] Tested edge cases (different types, None values)
- [x] **Validation**
  - [x] Ran existing test suite to ensure no regression
  - [x] Manual testing of comparison operations confirmed fix
  - [x] Code review completed

### 🔥 Day 2-3: Fix Optional Type Validation ✅ COMPLETED

- [x] **Analysis & Design**
  - [x] Analyzed current Union type validation logic
  - [x] Designed proper Optional type handling approach
  - [x] Chose Option A (proper fix with comprehensive Union support)
- [x] **Implementation - Comprehensive Fix**
  - [x] Added support for both `typing.Union` and `types.UnionType` in `validate_value_hint()`
  - [x] Properly handle `Union[T, None]` where value is `None`
  - [x] Ensured backward compatibility maintained
  - [x] Added contextlib.suppress for clean union type testing
- [x] **Testing**
  - [x] Created `tests/unit/test_optional_validation.py` with 14 comprehensive tests
  - [x] Tested `Optional[str] = None` ✅
  - [x] Tested `Optional[int] = 42` ✅
  - [x] Tested `Union[str, int]` with both types ✅
  - [x] Tested nested Optional types: `Optional[List[str]]` ✅
  - [x] Tested complex unions: `Union[str, int, None]` ✅
  - [x] Tested validation error messages ✅
- [x] **Files Modified**
  - [x] `classno/_validation.py` - Added Union type support
  - [x] Updated error handling and messages

### 🔥 Day 4-5: Add Missing Type Handlers ✅ COMPLETED

- [x] **Identified Missing Types**
  - [x] `frozenset` ✅
  - [x] `collections.deque` ✅
  - [x] `collections.defaultdict` ✅
  - [x] `collections.OrderedDict` ✅
  - [x] `collections.Counter` ✅
  - [x] Researched other commonly used collection types
- [x] **Added Validation Handlers**
  - [x] Implemented `validate_frozenset()`
  - [x] Implemented `validate_deque()`
  - [x] Reused existing handlers for dict-like collections
  - [x] Updated `VALIDATION_ORIGIN_HANDLER` dictionary
  - [x] Added fallback handler for unknown collection types
- [x] **Added Casting Handlers**
  - [x] Implemented `cast_frozenset()`
  - [x] Implemented `cast_deque()`
  - [x] Updated `CASTING_ORIGIN_HANDLER` dictionary
  - [x] Added fallback casting logic
  - [x] Fixed ValueError handling in casting operations
- [x] **Testing**
  - [x] Created `tests/unit/test_collection_types.py` with 16 comprehensive tests
  - [x] Tested validation for all new collection types ✅
  - [x] Tested autocasting for all new collection types ✅
  - [x] Tested nested structures with new types ✅
  - [x] Tested error handling for unsupported types ✅
- [x] **Files Modified**
  - [x] `classno/_validation.py` - Added collection type handlers
  - [x] `classno/_casting.py` - Added collection type handlers

### Phase 1 Results:

- **All unit tests**: 43/43 passed ✅
- **Working features test**: 18/18 passed ✅
- **Total regression tests**: 149/164 passed (91% pass rate)
- **Core functionality**: Fully restored and stable ✅

---

## Phase 2: High Priority Fixes (P1) - Week 2

### ⚠️ Day 1-2: Fix Shared Mutable Defaults

- [ ] **Analysis & Design**
  - [ ] Analyze current default value handling in `_hooks.py`
  - [ ] Choose between deep copy vs validation approach
  - [ ] Design backward compatibility strategy
  - [ ] make `__order_keys__`, `__eq__keys__`, `__hash_keys__` tuple type to preserve order
- [ ] **Implementation - Option A (Deep Copy)**
  - [ ] Modify `init_obj()` to deep copy mutable defaults
  - [ ] Add performance optimization for immutable types
  - [ ] Handle circular references safely
- [ ] **Implementation - Option B (Validation - Recommended)**
  - [ ] Create `validate_field_default()` function
  - [ ] Add validation in field creation process
  - [ ] Provide clear error messages with solutions
  - [ ] Add deprecation warnings for dangerous patterns
- [ ] **Testing**
  - [ ] Create `tests/unit/test_mutable_defaults.py`
  - [ ] Test that instances have independent default objects
  - [ ] Test list defaults: `field: List[str] = []`
  - [ ] Test dict defaults: `field: Dict[str, int] = {}`
  - [ ] Test set defaults: `field: Set[int] = set()`
  - [ ] Test performance impact of solution
  - [ ] Test error messages and warnings
- [ ] **Files to Modify**
  - [ ] `classno/_hooks.py`
  - [ ] `classno/_fields.py`

### ⚠️ Day 3: Fix Casting Return Issues

- [ ] **Code Analysis**
  - [ ] Identify all code paths in `cast_value()` that can return None
  - [ ] Review function contract and expected behavior
- [ ] **Implementation**
  - [ ] Add explicit return statements for all code paths
  - [ ] Add appropriate TypeError for uncautable types
  - [ ] Ensure function always returns a value or raises exception
  - [ ] Update docstring with clear contract
- [ ] **Testing**
  - [ ] Create `tests/unit/test_casting_returns.py`
  - [ ] Test all casting scenarios
  - [ ] Test edge cases that previously returned None
  - [ ] Test error conditions and exceptions
- [ ] **Files to Modify**
  - [ ] `classno/_casting.py`

### ⚠️ Day 4-5: Comprehensive Test Suite Development

- [ ] **Test Structure Setup**
  - [ ] Create directory structure: `tests/{unit,integration,edge_cases,regression}/`
  - [ ] Set up test configuration and utilities
  - [ ] Create test fixtures and helpers
- [ ] **Unit Tests**
  - [ ] `tests/unit/test_validation.py` - All validation logic
  - [ ] `tests/unit/test_casting.py` - All casting logic
  - [ ] `tests/unit/test_comparison.py` - Equality and ordering
  - [ ] `tests/unit/test_fields.py` - Field handling and defaults
  - [ ] `tests/unit/test_features.py` - Individual feature testing
- [ ] **Integration Tests**
  - [ ] `tests/integration/test_feature_combinations.py` - Multiple features together
  - [ ] `tests/integration/test_inheritance.py` - Class inheritance scenarios
  - [ ] `tests/integration/test_real_world_usage.py` - Realistic usage patterns
- [ ] **Edge Case Tests**
  - [ ] `tests/edge_cases/test_optional_types.py` - All Optional edge cases
  - [ ] `tests/edge_cases/test_union_types.py` - Complex Union scenarios
  - [ ] `tests/edge_cases/test_collection_types.py` - All collection edge cases
  - [ ] `tests/edge_cases/test_nested_structures.py` - Deep nesting scenarios
- [ ] **Regression Tests**
  - [ ] `tests/regression/test_bug_fixes.py` - Prevent bug reintroduction
  - [ ] Add specific test for each fixed bug
  - [ ] Document expected behavior vs previous broken behavior
- [ ] **Performance Tests**
  - [ ] `tests/performance/test_large_objects.py` - Large object handling
  - [ ] `tests/performance/test_many_fields.py` - Objects with many fields
  - [ ] `tests/performance/test_comparison_speed.py` - Comparison performance
- [ ] **Test Utilities**
  - [ ] Coverage reporting setup
  - [ ] Automated test running
  - [ ] Performance regression detection

---

## Phase 3: Medium Priority Fixes (P2) - Week 3

### 📝 Day 1-2: Standardize Error Messages

- [ ] **Design Error System**
  - [ ] Create `classno/_errors.py` module
  - [ ] Design `ErrorFormatter` class with standard methods
  - [ ] Define consistent error message templates
  - [ ] Plan migration strategy for existing error messages
- [ ] **Implementation**
  - [ ] Implement centralized error formatting
  - [ ] Update validation error messages
  - [ ] Update casting error messages
  - [ ] Update setattr error messages
  - [ ] Ensure consistent formatting across all modules
- [ ] **Testing**
  - [ ] Create `tests/unit/test_error_messages.py`
  - [ ] Test error message consistency
  - [ ] Test error message content and clarity
  - [ ] Test internationalization readiness
- [ ] **Files to Modify**
  - [ ] Create `classno/_errors.py`
  - [ ] `classno/_validation.py`
  - [ ] `classno/_setattrs.py`
  - [ ] `classno/_casting.py`

### 📝 Day 3-5: Code Review and Documentation

- [ ] **Code Review**
  - [ ] Review all changes made in Phases 1-2
  - [ ] Check for potential regressions
  - [ ] Verify test coverage is comprehensive
  - [ ] Review performance implications
- [ ] **Documentation Updates**
  - [ ] Add docstrings to all public functions
  - [ ] Update README with new behavior
  - [ ] Document breaking changes and migration guide
  - [ ] Update examples to follow best practices
- [ ] **Integration Testing**
  - [ ] Run full test suite
  - [ ] Test with real-world usage patterns
  - [ ] Verify backward compatibility where possible
  - [ ] Performance regression testing

---

## Phase 4: Polish & Release (P3) - Week 4

### ✨ Day 1: Performance Optimizations

- [ ] **Profiling**
  - [ ] Profile comparison operations
  - [ ] Profile field access patterns
  - [ ] Identify performance bottlenecks
- [ ] **Optimizations**
  - [ ] Cache `getattr` results in comparison functions where safe
  - [ ] Optimize hot paths in validation and casting
  - [ ] Consider lazy evaluation for expensive operations
  - [ ] Optimize memory usage in field storage
- [ ] **Performance Testing**
  - [ ] Benchmark before and after optimizations
  - [ ] Test with large objects and collections
  - [ ] Verify no performance regressions
- [ ] **Files to Modify**
  - [ ] `classno/_dunders.py`
  - [ ] `classno/_validation.py`
  - [ ] `classno/_casting.py`

### ✨ Day 2: Final Testing and Validation

- [ ] **Comprehensive Testing**
  - [ ] Run complete test suite with coverage reporting
  - [ ] Test all examples in `examples/` directory
  - [ ] Integration testing with popular libraries
  - [ ] Manual testing of common use cases
- [ ] **Regression Testing**
  - [ ] Test against previous version behavior
  - [ ] Ensure all identified bugs are fixed
  - [ ] Verify no new bugs introduced
- [ ] **Validation**
  - [ ] Code quality checks (linting, formatting)
  - [ ] Security vulnerability scanning
  - [ ] Compatibility testing across Python versions

### ✨ Day 3-4: Documentation and Examples

- [ ] **Fix Typos and Naming**
  - [ ] Rename `examples/copiyng.py` to `examples/copying.py`
  - [ ] Fix any other typos in comments and documentation
  - [ ] Update git history appropriately
- [ ] **Documentation Updates**
  - [ ] Update README.md with latest features and fixes
  - [ ] Create migration guide for breaking changes
  - [ ] Update API documentation
  - [ ] Add troubleshooting guide for common issues
- [ ] **Example Updates**
  - [ ] Review all examples for best practices
  - [ ] Add examples demonstrating fixed features
  - [ ] Ensure examples work with new version
  - [ ] Add complex real-world examples
- [ ] **Release Notes**
  - [ ] Document all bug fixes
  - [ ] Document any breaking changes
  - [ ] Document new features and improvements
  - [ ] Provide upgrade instructions

### ✨ Day 5: Release Preparation

- [ ] **Final Checks**
  - [ ] Version number update
  - [ ] Changelog finalization
  - [ ] License and copyright updates
  - [ ] Dependencies review and update

---

## Success Criteria Checklist

### Phase 1 (Critical) Success ✅ COMPLETED

- [x] All equality comparisons work correctly (`obj1 == obj2` returns False when values differ)
- [x] Optional types validate properly (`Optional[str] = None` works with validation)
- [x] No KeyError crashes on standard collection types (`frozenset`, `deque`, etc.)
- [x] All unit tests pass (43/43) and working features tests pass (18/18)
- [x] Core functionality restored with 91% pass rate on regression tests

### Phase 2 (High Priority) Success

- [ ] No shared mutable default issues (instances have independent defaults)
- [ ] Robust autocasting without implicit None returns
- [ ] Test coverage > 95%
- [ ] Performance regression tests pass
- [ ] All new features have comprehensive tests

### Final Release Success

- [ ] All 10 identified bugs fixed and tested
- [ ] Test coverage > 98%
- [ ] No breaking changes to public API (or clearly documented)
- [ ] Performance maintained or improved
- [ ] Documentation complete and accurate
- [ ] Examples work and demonstrate best practices
- [ ] Release notes and migration guide complete

---

## Risk Mitigation Checklist

### High-Risk Changes

- [ ] Optional type validation changes tested extensively
- [ ] Mutable defaults handling backward compatibility verified
- [ ] Feature flag system implemented for gradual rollout
- [ ] Rollback plan documented and tested

### Quality Assurance

- [ ] All changes code-reviewed
- [ ] Automated testing pipeline functioning
- [ ] Performance benchmarks in place
- [ ] Documentation reviewed for accuracy

### Communication

- [ ] Breaking changes clearly documented
- [ ] Migration guide provides clear instructions
- [ ] Deprecation warnings implemented where appropriate
- [ ] Community notified of upcoming changes

---

## Notes and Reminders

### Critical Dependencies

- Ensure `netsome` package compatibility for examples
- Test with different Python versions (3.10+)
- Verify typing compatibility across versions

### Documentation Requirements

- All public APIs must have docstrings
- Examples must be runnable and current
- Breaking changes must be clearly marked
- Migration path must be provided for incompatible changes

### Testing Standards

- Unit tests for all new functions
- Integration tests for feature interactions
- Regression tests for all bug fixes
- Performance tests for critical paths
- Edge case coverage for all type handling
