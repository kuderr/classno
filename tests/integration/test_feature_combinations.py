"""
Integration tests for feature combinations.

Tests how different classno features work together, ensuring
there are no conflicts or unexpected interactions.
"""

from typing import Dict
from typing import List
from typing import Optional
from typing import Set
from typing import Union

import pytest

from classno import Classno
from classno import Features
from classno import field


class TestFeatureCombinations:
    """Test various combinations of classno features."""

    def test_validation_with_casting(self):
        """Test VALIDATION + LOSSY_AUTOCAST combination."""
        class TestClass(Classno):
            __features__ = Features.VALIDATION | Features.LOSSY_AUTOCAST | Features.EQ
            name: str
            count: int
            items: List[str] = field(default_factory=list)

        # Should validate and then cast
        obj = TestClass(name="test", count="42", items=[1, 2, 3])
        assert obj.name == "test"
        assert obj.count == 42
        assert obj.items == ["1", "2", "3"]

    def test_eq_order_hash_combination(self):
        """Test EQ + ORDER + HASH feature combination."""
        class TestClass(Classno):
            __features__ = Features.EQ | Features.ORDER | Features.HASH
            name: str
            value: int

        obj1 = TestClass(name="alice", value=1)
        obj2 = TestClass(name="bob", value=2)
        obj3 = TestClass(name="alice", value=1)

        # Test equality
        assert obj1 == obj3
        assert obj1 != obj2

        # Test ordering
        assert obj1 < obj2  # "alice" < "bob"
        assert obj2 > obj1

        # Test hashing
        assert hash(obj1) == hash(obj3)
        obj_set = {obj1, obj2, obj3}
        assert len(obj_set) == 2  # obj1 and obj3 are the same

    def test_frozen_with_validation(self):
        """Test FROZEN + VALIDATION combination."""
        class TestClass(Classno):
            __features__ = Features.FROZEN | Features.VALIDATION | Features.EQ
            name: str
            count: int

        obj = TestClass(name="test", count=42)
        assert obj.name == "test"
        assert obj.count == 42

        # Should be frozen
        with pytest.raises(AttributeError):
            obj.name = "changed"

    def test_slots_with_hash(self):
        """Test SLOTS + HASH combination."""
        class TestClass(Classno):
            __features__ = Features.SLOTS | Features.HASH | Features.EQ
            name: str
            value: int

        obj = TestClass(name="test", value=42)

        # Should be hashable
        assert hash(obj) is not None

        # Should use slots (no __dict__)
        assert not hasattr(obj, '__dict__')

    def test_private_with_repr(self):
        """Test PRIVATE + REPR combination."""
        class TestClass(Classno):
            __features__ = Features.PRIVATE | Features.REPR | Features.EQ
            name: str
            _secret: str
            _private: int  # Single underscore to avoid Python name mangling

        obj = TestClass(name="test", _secret="hidden", _private=42)

        # Repr should not show private attributes
        repr_str = repr(obj)
        assert "name='test'" in repr_str
        assert "_secret" not in repr_str
        assert "_private" not in repr_str

    def test_immutable_feature_combination(self):
        """Test IMMUTABLE (combined feature)."""
        class TestClass(Classno):
            __features__ = Features.IMMUTABLE  # EQ | REPR | ORDER | HASH | SLOTS | FROZEN
            name: str
            value: int

        obj1 = TestClass(name="test", value=42)
        obj2 = TestClass(name="test", value=42)

        # All immutable features should work
        assert obj1 == obj2  # EQ
        assert repr(obj1)  # REPR
        assert obj1 <= obj2  # ORDER
        assert hash(obj1) == hash(obj2)  # HASH
        assert not hasattr(obj1, '__dict__')  # SLOTS

        # Should be frozen
        with pytest.raises(AttributeError):
            obj1.name = "changed"  # FROZEN

    def test_custom_keys_with_features(self):
        """Test custom keys with various features."""
        class TestClass(Classno):
            __features__ = Features.EQ | Features.ORDER | Features.HASH
            __eq_keys__ = ('id',)
            __order_keys__ = ('name', 'priority')
            __hash_keys__ = ('id',)

            id: int
            name: str
            priority: int
            data: str

        obj1 = TestClass(id=1, name="alice", priority=1, data="secret1")
        obj2 = TestClass(id=1, name="bob", priority=2, data="secret2")
        obj3 = TestClass(id=2, name="alice", priority=1, data="secret3")

        # Equality based on id only
        assert obj1 == obj2
        assert obj1 != obj3

        # Ordering based on name, priority
        assert obj1 < obj2  # "alice" < "bob"

        # Hashing based on id only
        assert hash(obj1) == hash(obj2)

    def test_validation_with_optional_types(self):
        """Test validation with Optional and Union types."""
        class TestClass(Classno):
            __features__ = Features.VALIDATION | Features.EQ
            name: str
            optional_count: Optional[int] = None
            flexible_value: Union[str, int] = "default"
            optional_list: Optional[List[str]] = None

        # Valid instances
        obj1 = TestClass(name="test")
        assert obj1.optional_count is None
        assert obj1.flexible_value == "default"
        assert obj1.optional_list is None

        obj2 = TestClass(
            name="test2",
            optional_count=42,
            flexible_value=100,
            optional_list=["a", "b"]
        )
        assert obj2.optional_count == 42
        assert obj2.flexible_value == 100
        assert obj2.optional_list == ["a", "b"]

    def test_casting_with_complex_types(self):
        """Test casting with complex nested types."""
        class TestClass(Classno):
            __features__ = Features.LOSSY_AUTOCAST | Features.EQ
            nested_dict: Dict[str, List[int]] = field(default_factory=dict)
            set_of_strings: Set[str] = field(default_factory=set)

        # Should cast nested structures
        obj = TestClass(
            nested_dict={"numbers": ["1", "2", "3"], "more": ["4", "5"]},
            set_of_strings=[1, 2, 3, 3]  # List with duplicates -> set of strings
        )

        assert obj.nested_dict == {"numbers": [1, 2, 3], "more": [4, 5]}
        assert obj.set_of_strings == {"1", "2", "3"}

    def test_all_features_combination(self):
        """Test a class with most features enabled."""
        class TestClass(Classno):
            __features__ = (
                Features.EQ | Features.ORDER | Features.HASH | Features.REPR |
                Features.VALIDATION | Features.LOSSY_AUTOCAST
            )

            name: str
            value: int
            items: List[str] = field(default_factory=list)

        obj1 = TestClass(name="test", value="42", items=[1, 2, 3])
        obj2 = TestClass(name="test", value="42", items=[1, 2, 3])

        # All features should work together
        assert obj1 == obj2  # EQ
        assert obj1 <= obj2  # ORDER
        assert hash(obj1) == hash(obj2)  # HASH
        assert repr(obj1)  # REPR
        assert obj1.value == 42  # VALIDATION + CASTING worked
        assert obj1.items == ["1", "2", "3"]  # VALIDATION + CASTING worked

    def test_feature_inheritance_interaction(self):
        """Test how features interact with inheritance."""
        class BaseClass(Classno):
            __features__ = Features.EQ | Features.VALIDATION
            name: str

        class DerivedClass(BaseClass):
            __features__ = Features.EQ | Features.VALIDATION | Features.ORDER
            value: int

        obj1 = DerivedClass(name="test", value=1)
        obj2 = DerivedClass(name="test", value=2)

        # Should have all features from both classes
        assert obj1 != obj2  # EQ works
        assert obj1 < obj2   # ORDER works
        # Validation should work for both base and derived fields

    def test_performance_with_multiple_features(self, performance_data):
        """Test performance doesn't degrade significantly with multiple features."""
        class TestClass(Classno):
            __features__ = Features.EQ | Features.ORDER | Features.HASH | Features.VALIDATION
            data: List[int] = field(default_factory=list)

        # Create objects with large data
        large_list = performance_data['large_list']
        obj1 = TestClass(data=large_list[:500])
        obj2 = TestClass(data=large_list[500:])

        # Operations should still be reasonably fast
        assert obj1 != obj2
        assert obj1 < obj2 or obj1 > obj2  # Some ordering
        assert hash(obj1) != hash(obj2)

    def test_error_handling_with_feature_combinations(self):
        """Test error handling when features are combined."""
        class TestClass(Classno):
            __features__ = Features.VALIDATION | Features.FROZEN | Features.EQ
            name: str
            count: int

        # Validation errors should still work with other features
        with pytest.raises(TypeError):
            TestClass(name="test", count="not_a_number")

        # Valid object should be frozen
        obj = TestClass(name="test", count=42)
        with pytest.raises(AttributeError):
            obj.name = "changed"

    def test_custom_keys_edge_cases(self):
        """Test edge cases with custom keys and features."""
        class TestClass(Classno):
            __features__ = Features.EQ | Features.ORDER | Features.HASH
            __eq_keys__ = ()  # Empty eq keys
            __order_keys__ = ('name',)
            __hash_keys__ = ('id',)

            id: int
            name: str

        obj1 = TestClass(id=1, name="alice")
        obj2 = TestClass(id=2, name="bob")

        # Empty eq_keys means all objects are equal
        assert obj1 == obj2

        # But ordering still works
        assert obj1 < obj2  # "alice" < "bob"

        # And hashing uses different key
        assert hash(obj1) != hash(obj2)
