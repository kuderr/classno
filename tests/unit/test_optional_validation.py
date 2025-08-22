"""
Tests for Optional type validation bug fix.
This ensures that Optional[T] and T | None types work correctly with validation.
"""

from typing import Dict
from typing import List
from typing import Optional
from typing import Union

import pytest

from classno import Classno
from classno import Features
from classno import field
from classno.exceptions import ValidationError


class TestOptionalValidation:
    """Test that Optional and Union types work correctly with validation."""

    def test_optional_with_none_default(self):
        """Test Optional fields with None as default value."""
        class OptionalModel(Classno):
            __features__ = Features.VALIDATION
            name: str
            optional_str: Optional[str] = None
            optional_int: Optional[int] = None
            optional_bool: Optional[bool] = None

        # Should work with None values
        obj = OptionalModel(name="test")
        assert obj.name == "test"
        assert obj.optional_str is None
        assert obj.optional_int is None
        assert obj.optional_bool is None

    def test_optional_with_actual_values(self):
        """Test Optional fields with actual values."""
        class OptionalModel(Classno):
            __features__ = Features.VALIDATION
            name: str
            optional_str: Optional[str] = None
            optional_int: Optional[int] = None

        # Should work with actual values
        obj = OptionalModel(name="test", optional_str="value", optional_int=42)
        assert obj.name == "test"
        assert obj.optional_str == "value"
        assert obj.optional_int == 42

    def test_new_union_syntax(self):
        """Test the new T | None syntax."""
        class NewSyntaxModel(Classno):
            __features__ = Features.VALIDATION
            name: str
            optional_str: str | None = None
            optional_int: int | None = None

        # Should work with None values
        obj1 = NewSyntaxModel(name="test")
        assert obj1.optional_str is None
        assert obj1.optional_int is None

        # Should work with actual values
        obj2 = NewSyntaxModel(name="test", optional_str="value", optional_int=42)
        assert obj2.optional_str == "value"
        assert obj2.optional_int == 42

    def test_complex_union_types(self):
        """Test complex Union types with multiple options."""
        class ComplexUnionModel(Classno):
            __features__ = Features.VALIDATION
            str_or_int: Union[str, int]
            str_int_or_none: Union[str, int, None] = None
            multiple_types: Union[str, int, float, bool]

        # Test str_or_int with string
        obj1 = ComplexUnionModel(str_or_int="hello", multiple_types="text")
        assert obj1.str_or_int == "hello"
        assert obj1.str_int_or_none is None
        assert obj1.multiple_types == "text"

        # Test str_or_int with int
        obj2 = ComplexUnionModel(str_or_int=42, multiple_types=3.14)
        assert obj2.str_or_int == 42
        assert obj2.multiple_types == 3.14

        # Test str_int_or_none with values
        obj3 = ComplexUnionModel(str_or_int=99, str_int_or_none="value", multiple_types=True)
        assert obj3.str_int_or_none == "value"
        assert obj3.multiple_types is True

    def test_optional_complex_types(self):
        """Test Optional with complex types like List, Dict."""
        class OptionalComplexModel(Classno):
            __features__ = Features.VALIDATION
            name: str
            optional_list: Optional[List[str]] = None
            optional_dict: Optional[Dict[str, int]] = None
            optional_tuple: Optional[tuple[int, str]] = None

        # Should work with None values
        obj1 = OptionalComplexModel(name="test")
        assert obj1.optional_list is None
        assert obj1.optional_dict is None
        assert obj1.optional_tuple is None

        # Should work with actual complex values
        obj2 = OptionalComplexModel(
            name="test",
            optional_list=["a", "b", "c"],
            optional_dict={"x": 1, "y": 2},
            optional_tuple=(42, "hello")
        )
        assert obj2.optional_list == ["a", "b", "c"]
        assert obj2.optional_dict == {"x": 1, "y": 2}
        assert obj2.optional_tuple == (42, "hello")

    def test_nested_optional_types(self):
        """Test nested Optional types."""
        class NestedOptionalModel(Classno):
            __features__ = Features.VALIDATION
            name: str
            # Optional list of optional strings
            optional_list_of_optionals: Optional[List[Optional[str]]] = None
            # Optional dict with optional values
            optional_dict_with_optionals: Optional[Dict[str, Optional[int]]] = None

        # Should work with None
        obj1 = NestedOptionalModel(name="test")
        assert obj1.optional_list_of_optionals is None
        assert obj1.optional_dict_with_optionals is None

        # Should work with nested optional values
        obj2 = NestedOptionalModel(
            name="test",
            optional_list_of_optionals=["hello", None, "world"],
            optional_dict_with_optionals={"a": 1, "b": None, "c": 3}
        )
        assert obj2.optional_list_of_optionals == ["hello", None, "world"]
        assert obj2.optional_dict_with_optionals == {"a": 1, "b": None, "c": 3}

    def test_invalid_optional_values(self):
        """Test that invalid values still raise ValidationError."""
        class OptionalModel(Classno):
            __features__ = Features.VALIDATION
            name: str
            optional_str: Optional[str] = None
            optional_int: Optional[int] = None

        # Should reject wrong types
        with pytest.raises(ValidationError):
            OptionalModel(name="test", optional_str=123)  # int instead of str

        with pytest.raises(ValidationError):
            OptionalModel(name="test", optional_int="not_int")  # str instead of int

    def test_invalid_union_values(self):
        """Test that invalid values for Union types raise ValidationError."""
        class UnionModel(Classno):
            __features__ = Features.VALIDATION
            str_or_int: Union[str, int]
            str_or_none: Optional[str] = None

        # Should reject types not in the union
        with pytest.raises(ValidationError):
            UnionModel(str_or_int=[1, 2, 3])  # list not in Union[str, int]

        with pytest.raises(ValidationError):
            UnionModel(str_or_int="hello", str_or_none=42)  # int not in Optional[str]

    def test_optional_with_field_factory(self):
        """Test Optional fields with field factory defaults."""
        class OptionalFieldModel(Classno):
            __features__ = Features.VALIDATION
            name: str
            optional_list: Optional[List[str]] = field(default=None)
            optional_with_factory: Optional[List[int]] = field(default_factory=lambda: None)
            required_with_factory: List[str] = field(default_factory=list)

        obj = OptionalFieldModel(name="test")
        assert obj.optional_list is None
        assert obj.optional_with_factory is None
        assert obj.required_with_factory == []

    def test_mixed_optional_and_required(self):
        """Test mixing optional and required fields."""
        class MixedModel(Classno):
            __features__ = Features.VALIDATION
            required_str: str
            required_int: int
            optional_str: Optional[str] = None
            optional_int: Optional[int] = None
            union_field: Union[str, int] = "default"

        # Should work with only required fields
        obj1 = MixedModel(required_str="hello", required_int=42)
        assert obj1.required_str == "hello"
        assert obj1.required_int == 42
        assert obj1.optional_str is None
        assert obj1.optional_int is None
        assert obj1.union_field == "default"

        # Should work with all fields
        obj2 = MixedModel(
            required_str="world",
            required_int=99,
            optional_str="optional",
            optional_int=123,
            union_field=456
        )
        assert obj2.optional_str == "optional"
        assert obj2.optional_int == 123
        assert obj2.union_field == 456

    def test_optional_custom_classes(self):
        """Test Optional with custom Classno classes."""
        class Address(Classno):
            __features__ = Features.VALIDATION
            street: str
            city: str

        class Person(Classno):
            __features__ = Features.VALIDATION
            name: str
            address: Optional[Address] = None

        # Should work with None address
        person1 = Person(name="John")
        assert person1.name == "John"
        assert person1.address is None

        # Should work with actual address
        address = Address(street="123 Main St", city="Boston")
        person2 = Person(name="Jane", address=address)
        assert person2.address.street == "123 Main St"
        assert person2.address.city == "Boston"

    def test_optional_validation_error_messages(self):
        """Test that validation error messages are helpful for Optional types."""
        class OptionalModel(Classno):
            __features__ = Features.VALIDATION
            name: str
            optional_str: Optional[str] = None

        try:
            OptionalModel(name="test", optional_str=123)
            assert False, "Should have raised ValidationError"
        except ValidationError as e:
            error_msg = str(e)
            assert "optional_str" in error_msg
            assert "123" in error_msg

    def test_union_validation_tries_all_types(self):
        """Test that Union validation tries all types in the union."""
        class UnionModel(Classno):
            __features__ = Features.VALIDATION
            flexible: Union[str, List[int], Dict[str, str]]

        # Should work with string
        obj1 = UnionModel(flexible="hello")
        assert obj1.flexible == "hello"

        # Should work with list of ints
        obj2 = UnionModel(flexible=[1, 2, 3])
        assert obj2.flexible == [1, 2, 3]

        # Should work with dict
        obj3 = UnionModel(flexible={"a": "x", "b": "y"})
        assert obj3.flexible == {"a": "x", "b": "y"}

        # Should fail with incompatible type
        with pytest.raises(ValidationError):
            UnionModel(flexible={"a": 1})  # dict with int values, not str values

    def test_optional_inheritance(self):
        """Test Optional types with inheritance."""
        class BaseModel(Classno):
            __features__ = Features.VALIDATION
            name: str
            optional_base: Optional[str] = None

        class ChildModel(BaseModel):
            age: int
            optional_child: Optional[int] = None

        # Should work with inherited optional
        child = ChildModel(name="test", age=25)
        assert child.name == "test"
        assert child.age == 25
        assert child.optional_base is None
        assert child.optional_child is None

        # Should work with values for both
        child2 = ChildModel(
            name="test2",
            age=30,
            optional_base="base_value",
            optional_child=42
        )
        assert child2.optional_base == "base_value"
        assert child2.optional_child == 42


if __name__ == "__main__":
    # Quick verification that the fix works
    from typing import Optional

    class QuickTest(Classno):
        __features__ = Features.VALIDATION
        name: str
        optional_field: Optional[str] = None

    obj = QuickTest(name="test")
    print(f"Created object with None optional: {obj}")

    obj2 = QuickTest(name="test2", optional_field="value")
    print(f"Created object with value: {obj2}")
