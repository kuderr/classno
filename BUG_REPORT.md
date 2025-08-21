# Classno Library Bug Report

## Critical Bugs Identified

### 🔴 **Bug #1: Equality Comparison Always Returns True**
**File:** `classno/_dunders.py:55`
**Severity:** Critical

**Issue:**
```python
def _cmp_factory(self, other: object, op: t.Callable[[t.Any, t.Any], bool], key: str) -> bool:
    if other.__class__ is not self.__class__:
        return NotImplemented

    self_key = getattr(self, key)()
    other_key = getattr(self, key)()  # BUG: Should be getattr(other, key)()

    return op(self_key, other_key)
```

**Problem:** Line 55 calls `getattr(self, key)()` for both `self_key` and `other_key`, meaning it's comparing `self` with itself instead of `self` with `other`.

**Impact:** All equality and ordering comparisons return incorrect results.

**Test Result:** 
```
obj1(value=1) == obj2(value=2): True  # Should be False!
```

**Fix:**
```python
other_key = getattr(other, key)()  # Change 'self' to 'other'
```

---

### 🔴 **Bug #2: Optional Type Validation Incorrectly Rejects None**
**File:** `classno/_validation.py:65-86`
**Severity:** Critical

**Issue:** The validation logic doesn't properly handle `typing.Optional[T]` types, treating them as `Union[T, NoneType]` but failing to validate `None` values correctly.

**Problem:** Optional types are implemented as `Union[T, None]` but the validation logic in `validate_value_hint` doesn't correctly handle the case where value is `None` for `Optional` types.

**Impact:** Cannot use Optional fields with None values when validation is enabled.

**Test Result:**
```
ValidationError for None in Optional: 
  - For field optional_value, expected typing.Optional[str] but got None of type <class 'NoneType'>;
```

**Root Cause:** The Union handling code tries each type in the union, but `None` doesn't validate against `NoneType` properly due to the isinstance check logic.

---

### 🔴 **Bug #3: Missing Validation Handlers for Several Types**  
**File:** `classno/_validation.py:57-62`
**Severity:** High

**Issue:** The `VALIDATION_ORIGIN_HANDLER` dictionary is missing handlers for several built-in collection types.

**Missing Types:**
- `frozenset`
- `collections.deque` 
- `collections.defaultdict`
- `collections.OrderedDict`
- Other collection types

**Test Result:**
```
KeyError for frozenset validation: <class 'frozenset'>
```

**Impact:** Runtime KeyError when using these types with validation enabled.

**Fix:** Add missing handlers or implement a fallback mechanism.

---

### 🟡 **Bug #4: Shared Mutable Default Values**
**File:** `classno/_hooks.py:15-16` and field handling
**Severity:** High

**Issue:** When using mutable objects as default values (instead of `default_factory`), all instances share the same mutable object.

**Problem:** The code directly assigns the default value without copying it:
```python
elif field.default is not c.MISSING:
    object.__setattr__(self, field.name, field.default)  # Shared reference!
```

**Test Result:**
```
BUG: Both objects share the same list instance!
obj1.tags after adding tag1: ['tag1']
obj2.tags after obj1 modification: ['tag1']
```

**Impact:** Unexpected behavior where modifying one instance affects others.

**Fix:** Use `copy.deepcopy()` for mutable defaults or warn/error on mutable defaults.

---

### 🟡 **Bug #5: Autocasting Can Return None Implicitly**
**File:** `classno/_casting.py:75-95`
**Severity:** Medium

**Issue:** The `cast_value` function has a code path that can return `None` implicitly.

**Problem:** If none of the conditions match, the function returns `None` implicitly:
```python
def cast_value(value, hint):
    # ... various conditions ...
    
    if isinstance(value, hint):
        return value
    # Missing return statement - returns None implicitly
```

**Impact:** Fields might be set to `None` unexpectedly during autocasting.

**Fix:** Add explicit return or raise appropriate exception.

---

### 🟡 **Bug #6: Unnecessary Return Value from setattr**
**File:** `classno/_setattrs.py:64`
**Severity:** Low

**Issue:** `setattr_processor` returns the result of `object.__setattr__()` which is always `None`.

**Problem:**
```python
def setattr_processor(self, name: str, value: t.Any) -> None:
    # ... processing ...
    return object.__setattr__(self, name, value)  # Always returns None
```

**Impact:** Inconsistent with Python's `__setattr__` which should not return a value.

**Fix:** Remove the `return` statement.

---

### 🟡 **Bug #7: Missing Casting Handlers**
**File:** `classno/_casting.py:67-72`  
**Severity:** Medium

**Issue:** Similar to validation, the `CASTING_ORIGIN_HANDLER` is missing handlers for many types.

**Missing Types:**
- `frozenset`
- `collections.deque`
- Other collection types

**Impact:** TypeError when attempting to autocast these types.

**Fix:** Add missing handlers or implement fallback logic.

---

## Minor Issues

### 🟢 **Issue #8: Inconsistent Error Messages**
**Files:** Various validation/casting files
**Severity:** Low

Different modules use inconsistent error message formats:
- `_validation.py`: "For field {field.name}, expected {field.hint} but got {attr!r} of type {type(attr)}"  
- `_setattrs.py`: "For field {field.name} expected type of {field.hint}, got {value} of type {type(value)}"

**Fix:** Standardize error message formats across the codebase.

---

### 🟢 **Issue #9: Typo in Example Filename**
**File:** `examples/copiyng.py`
**Severity:** Trivial

**Issue:** Filename should be `copying.py` not `copiyng.py`.

---

### 🟢 **Issue #10: TODO Comments in Production Code**
**Files:** `_feature_handlers.py:11, 59, 80`
**Severity:** Low

Several TODO comments remain in the codebase:
- `# TODO: move somewhere`
- `# TODO: dont override all of this if set by user`  
- `# TODO: should this two work together? if yes – in what order?`

**Fix:** Either implement the TODOs or remove them if they're no longer relevant.

---

## Code Quality Issues

### **CQ1: Type Annotation Inconsistencies**
Some functions lack proper type annotations or use inconsistent patterns.

### **CQ2: Missing Docstrings**
Most functions lack docstrings explaining their purpose and parameters.

### **CQ3: Error Handling**
Limited error handling in some edge cases, particularly around type conversion failures.

### **CQ4: Performance Considerations**
Repeated `getattr` calls in hot paths (like `_hash_value`, `_eq_value`) could be optimized.

---

## Recommendations

### **Immediate Action Required (Critical Bugs)**
1. **Fix Bug #1** immediately - this breaks basic equality comparison
2. **Fix Bug #2** - this breaks Optional type support with validation
3. **Fix Bug #3** - add missing validation handlers or graceful fallbacks

### **High Priority**
4. **Fix Bug #4** - implement proper mutable default handling
5. Add comprehensive test coverage for edge cases
6. Implement proper Union type validation logic

### **Medium Priority**  
7. Standardize error messages and improve error handling
8. Add missing type handlers for casting and validation
9. Address TODO comments and code quality issues

### **Low Priority**
10. Fix typos and improve documentation
11. Performance optimizations
12. Enhanced type annotations

---

## Test Coverage Gaps

The testing revealed several areas lacking adequate test coverage:
- Complex Union type validation
- Optional type edge cases  
- Error conditions and exception handling
- Feature interaction edge cases
- Performance with large objects/collections

## Impact Assessment

- **High Impact:** Bugs #1, #2, #3 affect core functionality
- **Medium Impact:** Bugs #4, #5, #7 affect specific use cases
- **Low Impact:** Issues #6, #8, #9, #10 are quality-of-life improvements

The most critical issues should be addressed immediately as they break fundamental expectations of the library.