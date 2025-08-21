# Classno Bug Fix TODO List

## Phase 1: Critical Fixes (P0) - Week 1

### 🔥 Day 1: Fix Equality Comparison Bug
- [ ] **Code Changes**
  - [ ] Fix `_dunders.py:55` - Change `getattr(self, key)()` to `getattr(other, key)()`
  - [ ] Review all comparison methods (`__eq__`, `__lt__`, `__le__`, `__gt__`, `__ge__`)
  - [ ] Ensure consistency across all comparison operations
  
- [ ] **Testing**
  - [ ] Create `tests/unit/test_comparison_fix.py`
  - [ ] Test basic equality: `obj1 == obj2` with different values
  - [ ] Test inequality: `obj1 != obj2` 
  - [ ] Test ordering: `obj1 < obj2`, `obj1 <= obj2`, `obj1 > obj2`, `obj1 >= obj2`
  - [ ] Test with custom `__eq_keys__` and `__order_keys__`
  - [ ] Test inheritance scenarios
  - [ ] Test edge cases (different types, None values)
  
- [ ] **Validation**
  - [ ] Run existing test suite to ensure no regression
  - [ ] Manual testing of comparison operations
  - [ ] Code review of changes

### 🔥 Day 2-3: Fix Optional Type Validation
- [ ] **Analysis & Design**
  - [ ] Analyze current Union type validation logic
  - [ ] Design proper Optional type handling approach
  - [ ] Choose between quick fix vs proper rewrite
  
- [ ] **Implementation - Option A (Quick Fix)**
  - [ ] Add special case handling for Optional types in `validate_value_hint()`
  - [ ] Handle `Union[T, None]` where value is `None`
  - [ ] Ensure backward compatibility
  
- [ ] **Implementation - Option B (Proper Fix)**
  - [ ] Create new `validate_union_type()` function
  - [ ] Rewrite Union validation logic comprehensively
  - [ ] Handle all Union edge cases
  
- [ ] **Testing**
  - [ ] Create `tests/unit/test_optional_validation.py`
  - [ ] Test `Optional[str] = None`
  - [ ] Test `Optional[int] = 42`
  - [ ] Test `Union[str, int]` with both types
  - [ ] Test nested Optional types: `Optional[List[str]]`
  - [ ] Test complex unions: `Union[str, int, None]`
  - [ ] Test validation error messages
  
- [ ] **Files to Modify**
  - [ ] `classno/_validation.py`
  - [ ] Update error handling and messages

### 🔥 Day 4-5: Add Missing Type Handlers
- [ ] **Identify Missing Types**
  - [ ] `frozenset`
  - [ ] `collections.deque`
  - [ ] `collections.defaultdict`
  - [ ] `collections.OrderedDict` 
  - [ ] `collections.Counter`
  - [ ] Research other commonly used collection types
  
- [ ] **Add Validation Handlers**
  - [ ] Implement `validate_frozenset()`
  - [ ] Implement `validate_deque()`
  - [ ] Reuse existing handlers for dict-like collections
  - [ ] Update `VALIDATION_ORIGIN_HANDLER` dictionary
  - [ ] Add fallback handler for unknown collection types
  
- [ ] **Add Casting Handlers**
  - [ ] Implement `cast_frozenset()`
  - [ ] Implement `cast_deque()`
  - [ ] Update `CASTING_ORIGIN_HANDLER` dictionary
  - [ ] Add fallback casting logic
  
- [ ] **Testing**
  - [ ] Create `tests/unit/test_collection_types.py`
  - [ ] Test validation for all new collection types
  - [ ] Test autocasting for all new collection types
  - [ ] Test nested structures with new types
  - [ ] Test error handling for unsupported types
  
- [ ] **Files to Modify**
  - [ ] `classno/_validation.py`
  - [ ] `classno/_casting.py`

---

## Phase 2: High Priority Fixes (P1) - Week 2

### ⚠️ Day 1-2: Fix Shared Mutable Defaults
- [ ] **Analysis & Design**
  - [ ] Analyze current default value handling in `_hooks.py`
  - [ ] Choose between deep copy vs validation approach
  - [ ] Design backward compatibility strategy
  
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

### 📝 Day 3: Remove Unnecessary Return Values & Address TODOs
- [ ] **Fix Unnecessary Returns**
  - [ ] Remove `return` from `setattr_processor()` in `_setattrs.py:64`
  - [ ] Review other functions for inappropriate return values
  - [ ] Update type annotations accordingly
  
- [ ] **Address TODO Comments**
  - [ ] Review `# TODO: move somewhere` in `_feature_handlers.py:11`
    - [ ] Evaluate if `set_keys()` function is in the right place
    - [ ] Move or document why it's there
  - [ ] Review `# TODO: dont override all of this if set by user` in `_feature_handlers.py:59`
    - [ ] Implement user override detection for dunder methods
    - [ ] Add tests for user-defined dunder methods
  - [ ] Review `# TODO: should this two work together?` in `_feature_handlers.py:80`
    - [ ] Document interaction between LOSSY_AUTOCAST and VALIDATION
    - [ ] Add tests for feature interaction
    - [ ] Update documentation
  
- [ ] **Testing**
  - [ ] Test that setattr doesn't return values inappropriately
  - [ ] Test user override scenarios
  - [ ] Test feature interaction behavior
  
- [ ] **Files to Modify**
  - [ ] `classno/_setattrs.py`
  - [ ] `classno/_feature_handlers.py`

### 📝 Day 4-5: Code Review and Documentation
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
  
- [ ] **Release Assets**
  - [ ] Build distribution packages
  - [ ] Test installation from packages
  - [ ] Prepare release announcements
  
- [ ] **Post-Release Planning**
  - [ ] Monitor for issues after release
  - [ ] Plan for hotfixes if needed
  - [ ] Schedule next development cycle

---

## Success Criteria Checklist

### Phase 1 (Critical) Success
- [ ] All equality comparisons work correctly (`obj1 == obj2` returns False when values differ)
- [ ] Optional types validate properly (`Optional[str] = None` works with validation)
- [ ] No KeyError crashes on standard collection types (`frozenset`, `deque`, etc.)
- [ ] All existing tests pass without modification
- [ ] No performance regression > 5%

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