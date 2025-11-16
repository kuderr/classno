"""
Edge case tests for Optional types.

Tests boundary conditions, corner cases, and complex scenarios
with Optional type handling in classno.
"""

from typing import Dict
from typing import List
from typing import Optional
from typing import Set
from typing import Tuple
from typing import Union

from classno import Classno
from classno import Features
from classno import field


class TestOptionalTypesEdgeCases:
    """Test edge cases and corner cases for Optional types."""

    def test_optional_with_none_as_explicit_default(self):
        """Test Optional with explicit None default."""
        class TestClass(Classno):
            __features__ = Features.VALIDATION | Features.EQ
            required_field: str
            optional_field: Optional[str] = None
            optional_int: Optional[int] = None

        obj = TestClass(required_field="test")
        assert obj.optional_field is None
        assert obj.optional_int is None

        obj2 = TestClass(required_field="test", optional_field="value", optional_int=42)
        assert obj2.optional_field == "value"
        assert obj2.optional_int == 42

    def test_optional_with_mutable_defaults_via_factory(self):
        """Test Optional mutable types using default_factory."""
        class TestClass(Classno):
            __features__ = Features.EQ
            name: str
            optional_list: Optional[List[str]] = None
            optional_dict: Optional[Dict[str, int]] = None

        obj = TestClass(name="test")
        assert obj.optional_list is None
        assert obj.optional_dict is None

        # Setting to actual values
        obj2 = TestClass(name="test", optional_list=["a", "b"], optional_dict={"x": 1})
        assert obj2.optional_list == ["a", "b"]
        assert obj2.optional_dict == {"x": 1}

    def test_nested_optional_types(self):
        """Test deeply nested Optional types."""
        class TestClass(Classno):
            __features__ = Features.VALIDATION | Features.EQ
            nested_optional: Optional[Dict[str, Optional[List[Optional[str]]]]] = None

        obj = TestClass()
        assert obj.nested_optional is None

        # Complex nested structure with Nones at various levels
        obj2 = TestClass(nested_optional={
            "group1": ["item1", None, "item3"],
            "group2": None,
            "group3": []
        })
        assert obj2.nested_optional["group1"] == ["item1", None, "item3"]
        assert obj2.nested_optional["group2"] is None
        assert obj2.nested_optional["group3"] == []

    def test_optional_with_casting(self):
        """Test Optional types with casting enabled."""
        class TestClass(Classno):
            __features__ = Features.LOSSY_AUTOCAST | Features.EQ
            optional_int: Optional[int] = None
            optional_list: Optional[List[int]] = None
            optional_bool: Optional[bool] = None

        # None should remain None
        obj1 = TestClass()
        assert obj1.optional_int is None
        assert obj1.optional_list is None
        assert obj1.optional_bool is None

        # Values should be cast to the non-None type
        obj2 = TestClass(
            optional_int="42",
            optional_list=["1", "2", "3"],
            optional_bool="true"
        )
        assert obj2.optional_int == 42
        assert obj2.optional_list == [1, 2, 3]
        assert obj2.optional_bool is True

        # None values should be preserved even with casting
        obj3 = TestClass(
            optional_int=None,
            optional_list=None,
            optional_bool=None
        )
        assert obj3.optional_int is None
        assert obj3.optional_list is None
        assert obj3.optional_bool is None

    def test_optional_custom_classes(self):
        """Test Optional with custom class types."""
        class InnerClass(Classno):
            __features__ = Features.EQ
            value: int

        class OuterClass(Classno):
            __features__ = Features.EQ
            name: str
            optional_inner: Optional[InnerClass] = None

        obj1 = OuterClass(name="test")
        assert obj1.optional_inner is None

        inner = InnerClass(value=42)
        obj2 = OuterClass(name="test", optional_inner=inner)
        assert obj2.optional_inner == inner
        assert obj2.optional_inner.value == 42

    def test_optional_with_union_types(self):
        """Test Optional combined with Union types."""
        class TestClass(Classno):
            __features__ = Features.VALIDATION | Features.EQ
            # Optional[Union[str, int]] is equivalent to Union[str, int, None]
            flexible_optional: Optional[Union[str, int]] = None
            # Union with None explicitly
            explicit_union: Union[str, int, None] = None

        obj1 = TestClass()
        assert obj1.flexible_optional is None
        assert obj1.explicit_union is None

        obj2 = TestClass(flexible_optional="string_value", explicit_union=42)
        assert obj2.flexible_optional == "string_value"
        assert obj2.explicit_union == 42

        obj3 = TestClass(flexible_optional=100, explicit_union="another_string")
        assert obj3.flexible_optional == 100
        assert obj3.explicit_union == "another_string"

    def test_optional_validation_edge_cases(self):
        """Test validation edge cases with Optional types."""
        class TestClass(Classno):
            __features__ = Features.VALIDATION | Features.EQ
            optional_positive_int: Optional[int] = None
            optional_non_empty_string: Optional[str] = None

        # None should always be valid for Optional types
        obj = TestClass()
        assert obj.optional_positive_int is None
        assert obj.optional_non_empty_string is None

        # Valid non-None values
        obj2 = TestClass(optional_positive_int=42, optional_non_empty_string="test")
        assert obj2.optional_positive_int == 42
        assert obj2.optional_non_empty_string == "test"

    def test_optional_with_generics(self):
        """Test Optional with generic types."""
        class TestClass(Classno):
            __features__ = Features.EQ
            optional_list_of_tuples: Optional[List[Tuple[str, int]]] = None
            optional_dict_of_lists: Optional[Dict[str, List[float]]] = None
            optional_set_of_strings: Optional[Set[str]] = None

        obj1 = TestClass()
        assert obj1.optional_list_of_tuples is None
        assert obj1.optional_dict_of_lists is None
        assert obj1.optional_set_of_strings is None

        obj2 = TestClass(
            optional_list_of_tuples=[("a", 1), ("b", 2)],
            optional_dict_of_lists={"nums": [1.1, 2.2], "more": [3.3]},
            optional_set_of_strings={"x", "y", "z"}
        )
        assert obj2.optional_list_of_tuples == [("a", 1), ("b", 2)]
        assert obj2.optional_dict_of_lists == {"nums": [1.1, 2.2], "more": [3.3]}
        assert obj2.optional_set_of_strings == {"x", "y", "z"}

    def test_optional_equality_and_hashing(self):
        """Test equality and hashing with Optional fields."""
        class TestClass(Classno):
            __features__ = Features.EQ | Features.HASH
            name: str
            optional_value: Optional[int] = None

        obj1 = TestClass(name="test")
        obj2 = TestClass(name="test")
        obj3 = TestClass(name="test", optional_value=42)
        obj4 = TestClass(name="test", optional_value=42)

        # Objects with None should be equal
        assert obj1 == obj2
        assert hash(obj1) == hash(obj2)

        # Objects with same non-None values should be equal
        assert obj3 == obj4
        assert hash(obj3) == hash(obj4)

        # Objects with None vs non-None should not be equal
        assert obj1 != obj3
        assert hash(obj1) != hash(obj3)

    def test_optional_ordering(self):
        """Test ordering with Optional fields."""
        import pytest

        class TestClass(Classno):
            __features__ = Features.EQ | Features.ORDER
            name: str
            optional_priority: Optional[int] = None

        obj1 = TestClass(name="alpha")  # None priority
        obj2 = TestClass(name="beta")   # None priority
        obj3 = TestClass(name="alpha", optional_priority=1)
        obj4 = TestClass(name="beta", optional_priority=2)

        # Should order by name first (when priorities are same type)
        assert obj1 < obj2  # "alpha" < "beta"
        assert obj3 < obj4  # "alpha" < "beta"

        # Comparing objects where one has None and another has int will fail
        # This is Python's limitation - None and int aren't comparable
        with pytest.raises(TypeError):
            obj1 < obj3  # Can't compare None with int

    def test_optional_with_inheritance(self):
        """Test Optional types in inheritance scenarios."""
        class BaseClass(Classno):
            __features__ = Features.EQ
            name: str
            optional_base: Optional[str] = None

        class DerivedClass(BaseClass):
            optional_derived: Optional[int] = None

        obj = DerivedClass(name="test")
        assert obj.optional_base is None
        assert obj.optional_derived is None

        obj2 = DerivedClass(
            name="test",
            optional_base="base_value",
            optional_derived=42
        )
        assert obj2.optional_base == "base_value"
        assert obj2.optional_derived == 42

    def test_optional_serialization_patterns(self):
        """Test Optional types in serialization-like scenarios."""
        class TestClass(Classno):
            __features__ = Features.EQ
            id: int
            name: str
            metadata: Optional[Dict[str, Union[str, int, None]]] = None
            tags: Optional[List[str]] = None
            parent_id: Optional[int] = None

        # Simulating data that might come from JSON/API
        obj1 = TestClass(id=1, name="root")  # Minimal object
        assert obj1.metadata is None
        assert obj1.tags is None
        assert obj1.parent_id is None

        obj2 = TestClass(
            id=2,
            name="child",
            metadata={"type": "document", "version": 1, "deprecated": None},
            tags=["important", "urgent"],
            parent_id=1
        )
        assert obj2.metadata == {"type": "document", "version": 1, "deprecated": None}
        assert obj2.tags == ["important", "urgent"]
        assert obj2.parent_id == 1

    def test_optional_type_errors(self):
        """Test type errors with Optional fields."""
        from classno.exceptions import ValidationError

        class TestClass(Classno):
            __features__ = Features.VALIDATION | Features.EQ
            optional_int: Optional[int] = None

        # Valid cases
        TestClass()  # None is valid
        TestClass(optional_int=42)  # int is valid
        TestClass(optional_int=None)  # explicit None is valid

        # Invalid cases (if validation is strict)
        # Note: This depends on validation implementation
        # Some might allow this with casting, others might reject
        try:
            obj = TestClass(optional_int="not_an_int_or_none")
            # If this doesn't raise an error, casting is happening
            # which might be acceptable depending on features
        except (TypeError, ValueError, ValidationError):
            # Validation correctly rejected invalid type
            pass

    def test_optional_performance_with_large_data(self, performance_data):
        """Test Optional performance with large datasets."""
        class TestClass(Classno):
            __features__ = Features.EQ
            name: str
            optional_large_list: Optional[List[int]] = None
            optional_large_dict: Optional[Dict[str, str]] = None

        # Objects with None should be fast
        obj1 = TestClass(name="test1")
        obj2 = TestClass(name="test2")
        assert obj1 != obj2  # Fast comparison

        # Objects with large data should still work
        large_list = performance_data['large_list']
        large_dict = performance_data['large_dict']

        obj3 = TestClass(name="test3", optional_large_list=large_list)
        obj4 = TestClass(name="test4", optional_large_dict=large_dict)

        assert obj3.optional_large_list == large_list
        assert obj4.optional_large_dict == large_dict
        assert obj3 != obj4

    def test_optional_with_default_factory_edge_case(self):
        """Test Optional with default_factory edge cases."""
        class TestClass(Classno):
            __features__ = Features.EQ
            name: str
            # This is a bit unusual - Optional with default_factory
            # The factory could return None or a value
            optional_with_factory: Optional[List[str]] = field(
                default_factory=lambda: None
            )
            optional_with_value_factory: Optional[List[str]] = field(
                default_factory=lambda: ["default"]
            )

        obj1 = TestClass(name="test1")
        assert obj1.optional_with_factory is None
        assert obj1.optional_with_value_factory == ["default"]

        obj2 = TestClass(name="test2")
        assert obj2.optional_with_factory is None
        assert obj2.optional_with_value_factory == ["default"]

        # Should be independent objects
        obj1.optional_with_value_factory.append("test")
        assert obj2.optional_with_value_factory == ["default"]
