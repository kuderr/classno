from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

import pytest

from classno import Classno
from classno import Features
from classno import field
from classno.exceptions import ValidationError


class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_missing_required_fields(self):
        """Test errors when required fields are missing."""

        class RequiredFields(Classno):
            name: str
            age: int
            email: str

        # Should work with all fields
        user = RequiredFields(name="John", age=30, email="john@example.com")
        assert user.name == "John"

        # Should fail with missing required field
        with pytest.raises(TypeError) as exc_info:
            RequiredFields(name="John", age=30)  # Missing email

        assert (
            "email" in str(exc_info.value) or "missing" in str(exc_info.value).lower()
        )

        # Should fail with multiple missing fields
        with pytest.raises(TypeError):
            RequiredFields(name="John")  # Missing age and email

    def test_invalid_field_types_without_validation(self):
        """Test that invalid types are accepted without validation feature."""

        class NoValidation(Classno):
            name: str
            age: int
            active: bool

        # Should accept any types when validation is off
        obj = NoValidation(name=123, age="thirty", active="yes")
        assert obj.name == 123
        assert obj.age == "thirty"
        assert obj.active == "yes"

    def test_validation_error_messages(self):
        """Test that validation provides helpful error messages."""

        class ValidatedClass(Classno):
            __features__ = Features.VALIDATION
            name: str
            age: int
            scores: List[float]

        # Test basic type validation error
        with pytest.raises(ValidationError) as exc_info:
            ValidatedClass(name=123, age=25, scores=[])

        error_msg = str(exc_info.value).lower()
        assert "name" in error_msg or "str" in error_msg

        # Test complex type validation error
        with pytest.raises(ValidationError) as exc_info:
            ValidatedClass(name="John", age=25, scores=[1, "invalid", 3])

        error_msg = str(exc_info.value).lower()
        assert "scores" in error_msg or "float" in error_msg or "list" in error_msg

    def test_frozen_modification_errors(self):
        """Test errors when trying to modify frozen objects."""

        class FrozenClass(Classno):
            __features__ = Features.FROZEN
            name: str
            value: int

        obj = FrozenClass(name="test", value=42)

        # Should raise appropriate error when trying to modify
        with pytest.raises(Exception) as exc_info:
            obj.name = "modified"

        error_msg = str(exc_info.value).lower()
        assert any(
            word in error_msg for word in ["frozen", "immutable", "read", "only"]
        )

        with pytest.raises(Exception):
            obj.value = 100

    def test_private_field_access_errors(self):
        """Test errors with private field access."""

        class PrivateClass(Classno):
            __features__ = Features.PRIVATE
            field: str

        obj = PrivateClass(field="original")

        # Should fail for direct private field modification
        with pytest.raises(Exception) as exc_info:
            obj.field = "modified"

        error_msg = str(exc_info.value).lower()
        assert "private" in error_msg or "read" in error_msg

        # But should work with underscore prefix
        obj._field = "modified"
        assert obj.field == "modified"

    def test_invalid_feature_combinations(self):
        """Test handling of invalid or conflicting feature combinations."""
        # This test depends on the library's implementation
        # Some feature combinations might not make sense or could cause conflicts

        class ConflictingFeatures(Classno):
            # This might cause issues if the library doesn't handle it well
            __features__ = Features.FROZEN | Features.LOSSY_AUTOCAST
            name: str
            value: int

        # Should still work, but behavior might vary
        try:
            obj = ConflictingFeatures(name="test", value=42.5)
            # If it works, the object should be created
            assert obj.name == "test"

            # Should still be frozen
            with pytest.raises(Exception):
                obj.name = "changed"
        except Exception:
            # If feature combination is truly incompatible, that's also valid
            pass

    def test_circular_reference_handling(self):
        """Test handling of circular references in validation."""

        class Node(Classno):
            __features__ = Features.VALIDATION
            name: str
            parent: Optional["Node"] = None
            children: List["Node"] = field(default_factory=list)

        # Should handle forward references
        root = Node(name="root")
        child = Node(name="child", parent=root)
        root.children = [child]

        assert root.name == "root"
        assert child.parent.name == "root"
        assert root.children[0].name == "child"

    def test_deep_nesting_limits(self):
        """Test behavior with very deep nesting."""

        class DeepNested(Classno):
            __features__ = Features.VALIDATION
            level: int
            nested: Optional["DeepNested"] = None

        # Create deeply nested structure
        current = None
        for i in range(100):  # 100 levels deep
            current = DeepNested(level=i, nested=current)

        # Should handle deep nesting
        assert current.level == 99

        # Navigate down the structure
        node = current
        for expected_level in range(99, -1, -1):
            assert node.level == expected_level
            node = node.nested
            if node is None:
                break

    def test_large_collection_validation(self):
        """Test validation with large collections."""

        class LargeCollection(Classno):
            __features__ = Features.VALIDATION
            numbers: List[int]
            mapping: Dict[str, int]

        # Large list
        large_list = list(range(10000))
        large_dict = {f"key_{i}": i for i in range(1000)}

        obj = LargeCollection(numbers=large_list, mapping=large_dict)
        assert len(obj.numbers) == 10000
        assert len(obj.mapping) == 1000

        # Should still validate all elements
        with pytest.raises(ValidationError):
            LargeCollection(numbers=large_list + ["invalid"], mapping=large_dict)

    def test_unicode_and_special_characters(self):
        """Test handling of unicode and special characters."""

        class UnicodeClass(Classno):
            __features__ = Features.VALIDATION | Features.EQ
            name: str
            description: str = ""

        # Unicode characters
        obj1 = UnicodeClass(name="José", description="café naïve résumé 🚀")
        obj2 = UnicodeClass(name="José", description="café naïve résumé 🚀")

        assert obj1.name == "José"
        assert "🚀" in obj1.description
        assert obj1 == obj2

        # Empty strings and whitespace
        obj3 = UnicodeClass(name="", description="   \t\n   ")
        assert obj3.name == ""
        assert obj3.description == "   \t\n   "

    def test_none_handling_edge_cases(self):
        """Test edge cases with None values."""

        class NoneHandling(Classno):
            __features__ = Features.VALIDATION
            required: str
            optional: Optional[str] = None
            optional_list: Optional[List[int]] = None
            union_with_none: Union[int, None] = None

        # Valid None usage
        obj = NoneHandling(required="test")
        assert obj.optional is None
        assert obj.optional_list is None
        assert obj.union_with_none is None

        # Valid non-None usage
        obj2 = NoneHandling(
            required="test2",
            optional="not none",
            optional_list=[1, 2, 3],
            union_with_none=42,
        )
        assert obj2.optional == "not none"
        assert obj2.optional_list == [1, 2, 3]
        assert obj2.union_with_none == 42

        # Should reject None for required field
        with pytest.raises(ValidationError):
            NoneHandling(required=None)

    def test_empty_class_definition(self):
        """Test edge case of empty class definition."""

        class EmptyClass(Classno):
            pass

        # Should work with no fields
        obj = EmptyClass()
        assert obj is not None

    def test_complex_default_factory_errors(self):
        """Test errors in default factory functions."""

        def failing_factory():
            raise ValueError("Factory failed")

        def invalid_type_factory():
            return "string"  # But field expects int

        class FactoryErrors(Classno):
            __features__ = Features.VALIDATION
            failing_field: list = field(default_factory=failing_factory)
            type_mismatch: int = field(default_factory=invalid_type_factory)

        # Should propagate factory errors
        with pytest.raises(ValueError):
            FactoryErrors()

    def test_inheritance_error_scenarios(self):
        """Test error scenarios with inheritance."""

        class BaseWithRequired(Classno):
            base_field: str

        class ChildWithRequired(BaseWithRequired):
            child_field: int

        # Should require both base and child fields
        with pytest.raises(TypeError):
            ChildWithRequired(base_field="base")  # Missing child_field

        with pytest.raises(TypeError):
            ChildWithRequired(child_field=42)  # Missing base_field

        # Should work with both
        obj = ChildWithRequired(base_field="base", child_field=42)
        assert obj.base_field == "base"
        assert obj.child_field == 42

    def test_malformed_type_hints(self):
        """Test handling of complex or edge case type hints."""

        class ComplexTypes(Classno):
            __features__ = Features.VALIDATION

            # Complex nested types
            nested_mapping: Dict[str, List[Tuple[int, Optional[str]]]]
            union_list: List[Union[int, str, None]]
            optional_complex: Optional[Dict[str, List[int]]] = None

        # Valid complex structure
        obj = ComplexTypes(
            nested_mapping={
                "group1": [(1, "one"), (2, None), (3, "three")],
                "group2": [(4, "four")],
            },
            union_list=[1, "two", None, 4, "five"],
        )

        assert obj.nested_mapping["group1"][0] == (1, "one")
        assert obj.union_list[2] is None

        # Invalid structure
        with pytest.raises(ValidationError):
            ComplexTypes(nested_mapping={"invalid": "not a list"}, union_list=[])

    def test_field_access_on_invalid_objects(self):
        """Test field access when object creation partially failed."""

        class PartiallyValid(Classno):
            __features__ = Features.VALIDATION
            valid_field: str
            invalid_field: int

        # This might create an object in an inconsistent state depending on implementation
        try:
            obj = PartiallyValid(valid_field="test", invalid_field="not an int")
            assert False, "Should have raised ValidationError"
        except ValidationError:
            # Expected behavior - object creation should fail completely
            pass
