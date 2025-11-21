"""Tests for validation edge cases and special scenarios."""

from collections.abc import Collection
from collections.abc import Sequence
from typing import Dict
from typing import List
from typing import Tuple
from typing import get_origin

import pytest

from classno import Classno
from classno import Features
from classno._validation import validate_dict
from classno._validation import validate_tuple
from classno._validation import validate_with_origin


class TestDictValidation:
    """Test dictionary validation edge cases."""

    def test_validate_dict_without_type_args(self):
        """Test validating dict with no type arguments."""
        value = {1: "a", 2: "b"}
        hint = Dict  # No type args

        # Should not raise - accepts any dict
        validate_dict(value, hint)

    def test_validate_dict_with_wrong_types(self):
        """Test dict validation fails with wrong types."""
        value = {"key": "not_int"}
        hint = Dict[str, int]

        with pytest.raises(TypeError):
            validate_dict(value, hint)


class TestTupleValidation:
    """Test tuple validation edge cases."""

    def test_validate_tuple_wrong_length(self):
        """Test tuple validation fails with wrong length."""
        value = (1, 2, 3)
        hint = Tuple[int, int]  # Expects 2 elements

        with pytest.raises(TypeError):
            validate_tuple(value, hint)

    def test_validate_tuple_with_ellipsis(self):
        """Test tuple validation with ellipsis accepts any length."""
        value = (1, 2, 3, 4, 5)
        hint = Tuple[int, ...]

        # Should not raise
        validate_tuple(value, hint)


class TestCollectionValidation:
    """Test collection validation with abstract types."""

    def test_validate_with_custom_iterable(self):
        """Test validation with custom iterable type."""

        class CustomIterable:
            def __init__(self, items):
                self.items = items

            def __iter__(self):
                return iter(self.items)

        class TestClass(Classno):
            __features__ = Features.VALIDATION
            data: List[int]

        obj = TestClass(data=[1, 2, 3])
        assert obj.data == [1, 2, 3]

    def test_validate_with_abstract_collection_type(self):
        """Test validation with abstract collection types uses fallback."""
        value = [1, 2, 3]
        hint = Collection[int]
        origin = get_origin(hint) or Collection

        # Should validate via fallback path
        validate_with_origin(value, hint, origin)

    def test_validate_non_iterable_custom_type(self):
        """Test validation with custom non-iterable type."""

        class CustomNonIterable:
            pass

        class TestClass(Classno):
            __features__ = Features.VALIDATION
            data: CustomNonIterable

        # Should work for the actual type
        obj = TestClass(data=CustomNonIterable())
        assert isinstance(obj.data, CustomNonIterable)

    def test_validate_unknown_non_iterable_origin_raises_error(self):
        """Test validation of unknown non-iterable origin raises error."""

        class NonIterableOrigin:
            pass

        value = NonIterableOrigin()
        hint = NonIterableOrigin
        origin = NonIterableOrigin

        with pytest.raises(TypeError) as exc_info:
            validate_with_origin(value, hint, origin)

        assert "No validation handler" in str(exc_info.value)


class TestIntegrationValidation:
    """Test validation in real Classno usage."""

    def test_validation_during_setattr(self):
        """Test validation occurs when setting attributes."""

        class ValidatedClass(Classno):
            __features__ = Features.VALIDATION
            age: int

        obj = ValidatedClass(age=25)

        # Valid update
        obj.age = 30
        assert obj.age == 30

        # Invalid update
        with pytest.raises(TypeError) as exc_info:
            obj.age = "not an int"

        assert "Validation error" in str(exc_info.value)

    def test_validation_with_abstract_collection(self):
        """Test validation with abstract collection types."""

        class TestClass(Classno):
            __features__ = Features.VALIDATION
            items: Sequence[int]

        # Sequence is abstract, should use fallback validation
        obj = TestClass(items=[1, 2, 3])
        assert obj.items == [1, 2, 3]
