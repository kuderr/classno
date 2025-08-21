#!/usr/bin/env python3
"""Test script to confirm identified bugs in classno library."""

import pytest
from classno import Classno, Features, field
from classno.exceptions import ValidationError
from typing import Optional, Union


def test_bug_1_dunders_comparison_issue():
    """Bug: _cmp_factory calls getattr(self, key)() instead of getattr(other, key)() for other_key."""
    
    class TestClass(Classno):
        __features__ = Features.EQ
        value: int
    
    obj1 = TestClass(value=1)
    obj2 = TestClass(value=2)
    
    # This should return False but might not work correctly due to the bug
    result = obj1 == obj2
    print(f"obj1(value=1) == obj2(value=2): {result}")
    
    # This should be True but the bug might make it behave incorrectly
    obj3 = TestClass(value=1)
    result2 = obj1 == obj3
    print(f"obj1(value=1) == obj3(value=1): {result2}")


def test_bug_2_optional_validation_issue():
    """Bug: Optional types validation incorrectly rejects None values."""
    
    class OptionalModel(Classno):
        __features__ = Features.VALIDATION
        name: str
        optional_value: Optional[str] = None
    
    try:
        # This should work but fails with ValidationError
        obj = OptionalModel(name="test")
        print(f"Created object with None optional: {obj}")
    except ValidationError as e:
        print(f"ValidationError for None in Optional: {e}")
    

def test_bug_3_validation_origin_missing():
    """Bug: VALIDATION_ORIGIN_HANDLER missing keys for complex types like frozenset."""
    
    class SetModel(Classno):
        __features__ = Features.VALIDATION
        data: frozenset[int]
    
    try:
        obj = SetModel(data=frozenset([1, 2, 3]))
        print(f"Created frozenset object: {obj}")
    except KeyError as e:
        print(f"KeyError for frozenset validation: {e}")
    except Exception as e:
        print(f"Other error for frozenset: {e}")


def test_bug_4_casting_return_none():
    """Bug: cast_value can return None in certain cases."""
    
    class CastModel(Classno):
        __features__ = Features.LOSSY_AUTOCAST
        value: int
    
    try:
        obj = CastModel(value="123")  # Should cast string to int
        print(f"Autocast string to int: {obj.value}")
        
        # Test edge case that might return None
        obj2 = CastModel(value=None)  # This might cause issues
        print(f"Autocast None: {obj2.value}")
    except Exception as e:
        print(f"Error in autocasting: {e}")


def test_bug_5_shared_mutable_defaults():
    """Bug: Mutable defaults are shared between instances."""
    
    class SharedDefaultsModel(Classno):
        tags: list[str] = []  # Dangerous mutable default
    
    obj1 = SharedDefaultsModel()
    obj2 = SharedDefaultsModel()
    
    obj1.tags.append("tag1")
    print(f"obj1.tags after adding tag1: {obj1.tags}")
    print(f"obj2.tags after obj1 modification: {obj2.tags}")
    
    if obj1.tags is obj2.tags:
        print("BUG: Both objects share the same list instance!")


def test_bug_6_setattr_processor_return():
    """Bug: setattr_processor returns the result of object.__setattr__ which is None."""
    
    class TestSetAttr(Classno):
        __features__ = Features.VALIDATION
        value: int
    
    obj = TestSetAttr(value=1)
    # This should not return anything, but the function returns None explicitly
    result = obj.__setattr__("value", 2)
    print(f"setattr returned: {result} (should not return anything)")


def test_bug_7_private_handler_validation_order():
    """Bug: Handler order in _setattrs.py might cause issues."""
    
    class PrivateValidated(Classno):
        __features__ = Features.PRIVATE | Features.VALIDATION
        secret: str
    
    obj = PrivateValidated(secret="test")
    
    try:
        # Try to set via private access
        obj._secret = "new_value"
        print(f"Private set worked: {obj.secret}")
        
        # Try to set directly (should fail)
        obj.secret = "direct_set"
        print("Direct set worked (unexpected!)")
    except Exception as e:
        print(f"Private/Validation interaction: {e}")


def test_bug_8_field_inheritance_issue():
    """Bug: Field inheritance might not work correctly with __fields__."""
    
    class BaseClass(Classno):
        base_field: str = "base"
    
    class ChildClass(BaseClass):
        child_field: str = "child"
    
    child = ChildClass()
    print(f"Child fields: {list(child.__fields__.keys())}")
    print(f"Base field accessible: {child.base_field}")
    print(f"Child field accessible: {child.child_field}")
    
    # Check if both classes share the same __fields__ dict
    if BaseClass.__fields__ is ChildClass.__fields__:
        print("BUG: Parent and child share same __fields__ dict!")


if __name__ == "__main__":
    print("=== Testing Bug 1: Comparison Issue ===")
    test_bug_1_dunders_comparison_issue()
    
    print("\n=== Testing Bug 2: Optional Validation ===")
    test_bug_2_optional_validation_issue()
    
    print("\n=== Testing Bug 3: Missing Validation Handlers ===")  
    test_bug_3_validation_origin_missing()
    
    print("\n=== Testing Bug 4: Casting Return None ===")
    test_bug_4_casting_return_none()
    
    print("\n=== Testing Bug 5: Shared Mutable Defaults ===")
    test_bug_5_shared_mutable_defaults()
    
    print("\n=== Testing Bug 6: SetAttr Return Value ===")
    test_bug_6_setattr_processor_return()
    
    print("\n=== Testing Bug 7: Handler Order ===")
    test_bug_7_private_handler_validation_order()
    
    print("\n=== Testing Bug 8: Field Inheritance ===")
    test_bug_8_field_inheritance_issue()