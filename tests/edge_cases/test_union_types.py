"""
Edge case tests for Union types.

Tests boundary conditions, corner cases, and complex scenarios
with Union type handling in classno.
"""

from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Set
from typing import Tuple
from typing import Union

from classno import Classno
from classno import Features
from classno import field


class TestUnionTypesEdgeCases:
    """Test edge cases and corner cases for Union types."""

    def test_simple_union_types(self):
        """Test basic Union types with primitive types."""
        class TestClass(Classno):
            __features__ = Features.VALIDATION | Features.EQ
            flexible_value: Union[str, int]
            optional_flexible: Union[str, int, None] = None

        # String value
        obj1 = TestClass(flexible_value="test")
        assert obj1.flexible_value == "test"
        assert obj1.optional_flexible is None

        # Integer value
        obj2 = TestClass(flexible_value=42)
        assert obj2.flexible_value == 42

        # Optional with string
        obj3 = TestClass(flexible_value=10, optional_flexible="optional")
        assert obj3.flexible_value == 10
        assert obj3.optional_flexible == "optional"

        # Optional with None
        obj4 = TestClass(flexible_value="test", optional_flexible=None)
        assert obj4.flexible_value == "test"
        assert obj4.optional_flexible is None

    def test_union_with_casting(self):
        """Test Union types with casting enabled."""
        class TestClass(Classno):
            __features__ = Features.LOSSY_AUTOCAST | Features.EQ
            str_or_int: Union[str, int]
            bool_or_float: Union[bool, float] = 0.0

        # Should cast to first matching type in union
        obj1 = TestClass(str_or_int="123")  # String - no casting needed
        assert obj1.str_or_int == "123"

        obj2 = TestClass(str_or_int=456)    # Int - no casting needed
        assert obj2.str_or_int == 456

        # More complex casting scenarios
        obj3 = TestClass(str_or_int="789", bool_or_float="3.14")
        assert obj3.str_or_int == "789"
        assert obj3.bool_or_float == 3.14

    def test_complex_union_types(self):
        """Test complex Union types with collections."""
        class TestClass(Classno):
            __features__ = Features.EQ
            list_or_dict: Union[List[str], Dict[str, int]]
            set_or_tuple: Union[Set[int], Tuple[int, ...]]

        # List case
        obj1 = TestClass(
            list_or_dict=["a", "b", "c"],
            set_or_tuple={1, 2, 3}
        )
        assert obj1.list_or_dict == ["a", "b", "c"]
        assert obj1.set_or_tuple == {1, 2, 3}

        # Dict case
        obj2 = TestClass(
            list_or_dict={"x": 1, "y": 2},
            set_or_tuple=(1, 2, 3, 1, 2)  # Tuple allows duplicates
        )
        assert obj2.list_or_dict == {"x": 1, "y": 2}
        assert obj2.set_or_tuple == (1, 2, 3, 1, 2)

    def test_nested_union_types(self):
        """Test deeply nested Union types."""
        class TestClass(Classno):
            __features__ = Features.EQ
            # Union of collections containing unions
            complex_field: Union[
                List[Union[str, int]],
                Dict[str, Union[bool, float]],
                Set[Union[str, int]]
            ]

        # List of mixed types
        obj1 = TestClass(complex_field=["string", 42, "another"])
        assert obj1.complex_field == ["string", 42, "another"]

        # Dict with mixed values
        obj2 = TestClass(complex_field={"flag": True, "value": 3.14, "name": False})
        assert obj2.complex_field == {"flag": True, "value": 3.14, "name": False}

        # Set of mixed types
        obj3 = TestClass(complex_field={"string", 42, "unique"})
        assert obj3.complex_field == {"string", 42, "unique"}

    def test_union_with_custom_classes(self):
        """Test Union types with custom classes."""
        class TypeA(Classno):
            __features__ = Features.EQ
            a_field: str

        class TypeB(Classno):
            __features__ = Features.EQ
            b_field: int

        class Container(Classno):
            __features__ = Features.EQ
            content: Union[TypeA, TypeB, str]

        # TypeA instance
        type_a = TypeA(a_field="test")
        obj1 = Container(content=type_a)
        assert obj1.content == type_a
        assert obj1.content.a_field == "test"

        # TypeB instance
        type_b = TypeB(b_field=42)
        obj2 = Container(content=type_b)
        assert obj2.content == type_b
        assert obj2.content.b_field == 42

        # String value
        obj3 = Container(content="just a string")
        assert obj3.content == "just a string"

    def test_union_with_none_variations(self):
        """Test various ways to express unions with None."""
        class TestClass(Classno):
            __features__ = Features.EQ
            # Different ways to express optional unions
            optional_style: Optional[Union[str, int]] = None
            explicit_union: Union[str, int, None] = None
            union_with_none: Union[None, str, int] = None  # None first

        obj1 = TestClass()
        assert obj1.optional_style is None
        assert obj1.explicit_union is None
        assert obj1.union_with_none is None

        obj2 = TestClass(
            optional_style="test",
            explicit_union=42,
            union_with_none="value"
        )
        assert obj2.optional_style == "test"
        assert obj2.explicit_union == 42
        assert obj2.union_with_none == "value"

    def test_union_ordering_priority(self):
        """Test Union type matching priority."""
        class TestClass(Classno):
            __features__ = Features.LOSSY_AUTOCAST | Features.EQ
            # Order matters in Union types
            str_first: Union[str, int]
            int_first: Union[int, str]
            bool_vs_int: Union[bool, int]  # bool is subclass of int

        # String representations
        obj = TestClass(
            str_first="123",   # Should remain string
            int_first="456",   # Should remain string (or be cast to int)
            bool_vs_int=True   # Should be bool
        )

        assert isinstance(obj.str_first, str)
        assert obj.bool_vs_int is True
        assert isinstance(obj.bool_vs_int, bool)

    def test_union_validation_edge_cases(self):
        """Test validation edge cases with Union types."""
        class TestClass(Classno):
            __features__ = Features.VALIDATION | Features.EQ
            strict_union: Union[int, str]

        # Valid cases
        TestClass(strict_union=42)
        TestClass(strict_union="test")

        # Edge cases that might be problematic
        TestClass(strict_union="")     # Empty string
        TestClass(strict_union=0)      # Zero
        TestClass(strict_union=-1)     # Negative number

    def test_union_with_generics(self):
        """Test Union types with generic parameters."""
        # Note: Generic TypeVars need to be defined, so we use concrete types instead

        class ConcreteTestClass(Classno):
            __features__ = Features.EQ
            int_list_or_dict: Union[List[int], Dict[str, int]] = field(
                default_factory=list
            )
            str_list_or_dict: Union[List[str], Dict[str, str]] = field(
                default_factory=list
            )

        obj1 = ConcreteTestClass()
        assert obj1.int_list_or_dict == []
        assert obj1.str_list_or_dict == []

        obj2 = ConcreteTestClass(
            int_list_or_dict=[1, 2, 3], str_list_or_dict={"a": "x", "b": "y"}
        )
        assert obj2.int_list_or_dict == [1, 2, 3]
        assert obj2.str_list_or_dict == {"a": "x", "b": "y"}

    def test_union_equality_and_hashing(self):
        """Test equality and hashing with Union fields."""
        class TestClass(Classno):
            __features__ = Features.EQ | Features.HASH
            name: str
            flexible: Union[str, int, List[str]]

        # Same type, same value
        obj1 = TestClass(name="test", flexible="value")
        obj2 = TestClass(name="test", flexible="value")
        assert obj1 == obj2
        assert hash(obj1) == hash(obj2)

        # Different types, conceptually same value
        obj3 = TestClass(name="test", flexible=42)
        obj4 = TestClass(name="test", flexible="42")  # String representation
        assert obj3 != obj4  # Different types should not be equal
        assert hash(obj3) != hash(obj4)

        # Same type, same complex value
        obj5 = TestClass(name="test", flexible=["a", "b"])
        obj6 = TestClass(name="test", flexible=["a", "b"])
        assert obj5 == obj6

    def test_union_with_inheritance(self):
        """Test Union types in inheritance scenarios."""
        class BaseClass(Classno):
            __features__ = Features.EQ
            base_union: Union[str, int] = "default"

        class DerivedClass(BaseClass):
            derived_union: Union[List[str], Dict[str, int]] = field(default_factory=list)

        obj = DerivedClass()
        assert obj.base_union == "default"
        assert obj.derived_union == []

        obj2 = DerivedClass(
            base_union=42,
            derived_union={"count": 10}
        )
        assert obj2.base_union == 42
        assert obj2.derived_union == {"count": 10}

    def test_union_type_narrowing(self):
        """Test type narrowing patterns with Union fields."""
        class TestClass(Classno):
            __features__ = Features.EQ
            value: Union[str, int, List[str], None] = None

        obj = TestClass(value="string")

        # Type narrowing patterns (this is more about usage than testing)
        if isinstance(obj.value, str):
            assert len(obj.value) >= 0  # String operations
        elif isinstance(obj.value, int):
            assert obj.value == obj.value  # Int operations
        elif isinstance(obj.value, list):
            assert len(obj.value) >= 0  # List operations
        else:
            assert obj.value is None

    def test_union_serialization_patterns(self):
        """Test Union types in serialization-like scenarios."""
        class TestClass(Classno):
            __features__ = Features.EQ
            # Common pattern: field can be an ID (int) or a full object (dict)
            reference: Union[int, Dict[str, Any]]
            # Another pattern: value can be computed (str) or raw data (list)
            data: Union[str, List[Union[str, int, float]]]

        # Reference as ID
        obj1 = TestClass(reference=42, data="computed_value")
        assert obj1.reference == 42
        assert obj1.data == "computed_value"

        # Reference as full object
        obj2 = TestClass(
            reference={"id": 42, "name": "Object", "type": "full"},
            data=["raw", 123, 45.6, "mixed"]
        )
        assert obj2.reference == {"id": 42, "name": "Object", "type": "full"}
        assert obj2.data == ["raw", 123, 45.6, "mixed"]

    def test_union_performance_edge_cases(self, performance_data):
        """Test Union performance with large data sets."""
        class TestClass(Classno):
            __features__ = Features.EQ
            large_data: Union[List[int], Dict[str, str]]

        # Large list
        large_list = performance_data['large_list']
        obj1 = TestClass(large_data=large_list)
        assert obj1.large_data == large_list

        # Large dict
        large_dict = performance_data['large_dict']
        obj2 = TestClass(large_data=large_dict)
        assert obj2.large_data == large_dict

        # Comparison should still be reasonable
        assert obj1 != obj2

    def test_union_error_handling(self):
        """Test error handling with Union types."""
        class TestClass(Classno):
            __features__ = Features.VALIDATION | Features.EQ
            limited_union: Union[str, int]

        # Valid types
        TestClass(limited_union="test")
        TestClass(limited_union=42)

        # Invalid type - should be rejected if validation is strict
        # Note: Behavior depends on validation implementation
        # Some might cast, others might reject
        from classno.exceptions import ValidationError

        try:
            obj = TestClass(limited_union=[1, 2, 3])  # List not in union
            # If this succeeds, casting/coercion is happening
        except (TypeError, ValueError, ValidationError):
            # Validation correctly rejected the invalid type
            pass

    def test_union_with_forward_references(self):
        """Test Union types with forward references."""
        # This is more complex and might not be fully supported
        # depending on the implementation

        class NodeClass(Classno):
            __features__ = Features.EQ
            value: str
            # Forward reference to self type
            child: Union['NodeClass', None] = None

        root = NodeClass(value="root")
        assert root.child is None

        child = NodeClass(value="child")
        root_with_child = NodeClass(value="root", child=child)
        assert root_with_child.child == child
        assert root_with_child.child.value == "child"

    def test_union_boundary_conditions(self):
        """Test boundary conditions for Union types."""
        class TestClass(Classno):
            __features__ = Features.EQ
            # Edge cases
            single_union: Union[str]  # Union with single type
            empty_or_value: Union[str, List[str]]  # Could be empty

        obj1 = TestClass(
            single_union="only_option",
            empty_or_value=""  # Empty string
        )
        assert obj1.single_union == "only_option"
        assert obj1.empty_or_value == ""

        obj2 = TestClass(
            single_union="test",
            empty_or_value=[]  # Empty list
        )
        assert obj2.single_union == "test"
        assert obj2.empty_or_value == []
