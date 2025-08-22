"""
Tests for the equality comparison bug fix.
This ensures that the _cmp_factory function correctly compares self with other,
not self with self.
"""

import pytest
from classno import Classno, Features


class TestComparisonFix:
    """Test that comparison operations work correctly after the bug fix."""
    
    def test_basic_equality_with_different_values(self):
        """Test that objects with different values are not equal."""
        class TestClass(Classno):
            __features__ = Features.EQ
            value: int
        
        obj1 = TestClass(value=1)
        obj2 = TestClass(value=2)
        
        # This was returning True before the fix (BUG)
        assert obj1 != obj2
        assert not (obj1 == obj2)
    
    def test_basic_equality_with_same_values(self):
        """Test that objects with same values are equal."""
        class TestClass(Classno):
            __features__ = Features.EQ
            value: int
        
        obj1 = TestClass(value=1)
        obj2 = TestClass(value=1)
        
        assert obj1 == obj2
        assert not (obj1 != obj2)
    
    def test_equality_with_multiple_fields(self):
        """Test equality with multiple fields."""
        class TestClass(Classno):
            __features__ = Features.EQ
            name: str
            age: int
            active: bool
        
        obj1 = TestClass(name="Alice", age=30, active=True)
        obj2 = TestClass(name="Alice", age=30, active=True)
        obj3 = TestClass(name="Bob", age=30, active=True)
        obj4 = TestClass(name="Alice", age=25, active=True)
        obj5 = TestClass(name="Alice", age=30, active=False)
        
        # Same values should be equal
        assert obj1 == obj2
        
        # Different values should not be equal
        assert obj1 != obj3  # Different name
        assert obj1 != obj4  # Different age
        assert obj1 != obj5  # Different active
    
    def test_custom_eq_keys(self):
        """Test equality with custom __eq_keys__."""
        class TestClass(Classno):
            __features__ = Features.EQ
            __eq_keys__ = {"id"}
            
            id: int
            name: str
            description: str
        
        obj1 = TestClass(id=1, name="Alice", description="First")
        obj2 = TestClass(id=1, name="Bob", description="Second")  # Same ID
        obj3 = TestClass(id=2, name="Alice", description="First")  # Different ID
        
        # Should be equal based only on ID
        assert obj1 == obj2
        
        # Should not be equal due to different ID
        assert obj1 != obj3
    
    def test_ordering_operations(self):
        """Test that ordering operations work correctly."""
        class TestClass(Classno):
            __features__ = Features.ORDER
            value: int
        
        obj1 = TestClass(value=1)
        obj2 = TestClass(value=2)
        obj3 = TestClass(value=3)
        
        # Less than
        assert obj1 < obj2
        assert obj2 < obj3
        assert not (obj2 < obj1)
        
        # Less than or equal
        assert obj1 <= obj2
        assert obj1 <= TestClass(value=1)  # Equal case
        assert not (obj2 <= obj1)
        
        # Greater than
        assert obj2 > obj1
        assert obj3 > obj2
        assert not (obj1 > obj2)
        
        # Greater than or equal
        assert obj2 >= obj1
        assert obj1 >= TestClass(value=1)  # Equal case
        assert not (obj1 >= obj2)
    
    def test_custom_order_keys(self):
        """Test ordering with custom __order_keys__."""
        class TestClass(Classno):
            __features__ = Features.ORDER
            __order_keys__ = {"id"}  # Use single key to avoid order issues
            
            id: int
            name: str
            description: str
        
        obj1 = TestClass(id=1, name="first", description="First")
        obj2 = TestClass(id=2, name="second", description="Second")
        obj3 = TestClass(id=3, name="third", description="Third")
        
        # Should order by ID only, ignoring name and description
        assert obj1 < obj2
        assert obj2 < obj3
        assert obj1 < obj3
        
        # Test that name and description don't affect ordering
        obj_same_id = TestClass(id=2, name="different", description="Different")
        assert not (obj2 < obj_same_id)  # Same ID
        assert not (obj_same_id < obj2)  # Same ID
        
        # Test sorting
        items = [obj3, obj1, obj2]
        sorted_items = sorted(items)
        assert sorted_items == [obj1, obj2, obj3]
    
    def test_combined_eq_and_order_features(self):
        """Test that EQ and ORDER features work together."""
        class TestClass(Classno):
            __features__ = Features.EQ | Features.ORDER
            value: int
        
        obj1 = TestClass(value=1)
        obj2 = TestClass(value=1)
        obj3 = TestClass(value=2)
        
        # Equality
        assert obj1 == obj2
        assert obj1 != obj3
        
        # Ordering
        assert obj1 < obj3
        assert obj1 <= obj2  # Equal case
        assert obj3 > obj1
        assert obj2 >= obj1  # Equal case
    
    def test_different_classes_return_not_implemented(self):
        """Test that comparing different classes returns NotImplemented."""
        class TestClass1(Classno):
            __features__ = Features.EQ
            value: int
        
        class TestClass2(Classno):
            __features__ = Features.EQ
            value: int
        
        obj1 = TestClass1(value=1)
        obj2 = TestClass2(value=1)
        
        # Should return NotImplemented, which Python converts to False for ==
        # and True for !=
        assert obj1 != obj2
        assert not (obj1 == obj2)
    
    def test_inheritance_comparison(self):
        """Test comparison with class inheritance."""
        class BaseClass(Classno):
            __features__ = Features.EQ
            base_value: int
        
        class ChildClass(BaseClass):
            child_value: str
        
        parent = BaseClass(base_value=1)
        child1 = ChildClass(base_value=1, child_value="test")
        child2 = ChildClass(base_value=1, child_value="test")
        child3 = ChildClass(base_value=2, child_value="test")
        
        # Child instances with same values should be equal
        assert child1 == child2
        
        # Child instances with different values should not be equal
        assert child1 != child3
        
        # Parent and child are different classes, should not be equal
        assert parent != child1
    
    def test_edge_cases_with_none_values(self):
        """Test comparison with None values in fields."""
        class TestClass(Classno):
            __features__ = Features.EQ
            name: str
            optional_value: str | None = None
        
        obj1 = TestClass(name="test", optional_value=None)
        obj2 = TestClass(name="test", optional_value=None)
        obj3 = TestClass(name="test", optional_value="value")
        
        assert obj1 == obj2  # Both have None
        assert obj1 != obj3  # One has None, other has value
    
    def test_hash_consistency_with_equality(self):
        """Test that hash values are consistent with equality."""
        class TestClass(Classno):
            __features__ = Features.EQ | Features.HASH
            value: int
        
        obj1 = TestClass(value=1)
        obj2 = TestClass(value=1)
        obj3 = TestClass(value=2)
        
        # Equal objects should have equal hashes
        assert obj1 == obj2
        assert hash(obj1) == hash(obj2)
        
        # Unequal objects should have different hashes (usually)
        assert obj1 != obj3
        # Note: Hash inequality is not guaranteed, but very likely
        assert hash(obj1) != hash(obj3)
    
    def test_custom_hash_keys_with_equality(self):
        """Test custom hash keys work with equality comparison."""
        class TestClass(Classno):
            __features__ = Features.EQ | Features.HASH
            __eq_keys__ = {"id"}
            __hash_keys__ = {"id"}
            
            id: int
            name: str
        
        obj1 = TestClass(id=1, name="Alice")
        obj2 = TestClass(id=1, name="Bob")  # Same ID, different name
        obj3 = TestClass(id=2, name="Alice")  # Different ID
        
        # Should be equal based on ID only
        assert obj1 == obj2
        assert hash(obj1) == hash(obj2)
        
        # Should not be equal due to different ID
        assert obj1 != obj3
        assert hash(obj1) != hash(obj3)
    
    def test_reflexivity_symmetry_transitivity(self):
        """Test mathematical properties of equality."""
        class TestClass(Classno):
            __features__ = Features.EQ
            value: int
        
        obj1 = TestClass(value=1)
        obj2 = TestClass(value=1)
        obj3 = TestClass(value=1)
        
        # Reflexivity: x == x
        assert obj1 == obj1
        
        # Symmetry: if x == y then y == x
        assert obj1 == obj2
        assert obj2 == obj1
        
        # Transitivity: if x == y and y == z then x == z
        assert obj1 == obj2
        assert obj2 == obj3
        assert obj1 == obj3


if __name__ == "__main__":
    # Quick verification that the fix works
    class QuickTest(Classno):
        __features__ = Features.EQ
        value: int
    
    obj1 = QuickTest(value=1)
    obj2 = QuickTest(value=2)
    
    print(f"obj1(value=1) == obj2(value=2): {obj1 == obj2}")  # Should be False
    print(f"obj1(value=1) != obj2(value=2): {obj1 != obj2}")  # Should be True
    
    obj3 = QuickTest(value=1)
    print(f"obj1(value=1) == obj3(value=1): {obj1 == obj3}")  # Should be True