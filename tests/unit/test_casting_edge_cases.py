"""Tests for casting edge cases and special scenarios."""

from typing import List
from typing import Mapping
from typing import Union

import pytest

from classno import Classno
from classno import Features
from classno._casting import cast_bool_from_string
from classno._casting import cast_union
from classno._casting import cast_value
from classno._casting import cast_with_origin


class TestBooleanCasting:
    """Test boolean casting from strings."""

    def test_cast_bool_from_true_strings(self):
        """Test casting various true representations."""
        assert cast_bool_from_string("true") is True
        assert cast_bool_from_string("TRUE") is True
        assert cast_bool_from_string("1") is True
        assert cast_bool_from_string("yes") is True

    def test_cast_bool_from_false_strings(self):
        """Test casting various false representations."""
        assert cast_bool_from_string("false") is False
        assert cast_bool_from_string("FALSE") is False
        assert cast_bool_from_string("0") is False
        assert cast_bool_from_string("no") is False
        assert cast_bool_from_string("") is False  # Empty string is false

    def test_cast_bool_from_invalid_string_raises_error(self):
        """Test casting invalid string to bool raises error."""
        with pytest.raises(TypeError) as exc_info:
            cast_bool_from_string("maybe")

        assert "Cannot cast" in str(exc_info.value)
        assert "maybe" in str(exc_info.value)


class TestUnionCasting:
    """Test union type casting edge cases."""

    def test_cast_union_with_none_already_none(self):
        """Test casting None to Optional returns None immediately."""
        hint = Union[int, None]
        result = cast_union(None, hint)
        assert result is None

    def test_cast_union_value_already_matches_type(self):
        """Test union returns value if already matches a type."""
        hint = Union[int, str]
        result = cast_union(42, hint)
        assert result == 42

    def test_cast_union_container_matches_but_cast_fails(self):
        """Test union with container that matches but inner cast fails."""
        hint = Union[str, List[int]]
        value = ["not", "ints"]  # List but wrong inner types

        result = cast_union(value, hint)
        # Should return the list as-is since container matches
        assert isinstance(result, list)

    def test_cast_union_skip_none_during_casting(self):
        """Test union skips None type when value is not None."""
        # None is first, but value is not None, should skip and cast to int
        hint = Union[None, int]
        value = "123"

        result = cast_union(value, hint)
        assert result == 123

    def test_cast_union_with_multiple_types(self):
        """Test union tries multiple types in order."""
        hint = Union[dict, None, int, str]
        value = 42.5  # Float

        result = cast_union(value, hint)
        assert result == 42  # Cast to int


class TestGenericCasting:
    """Test casting with generic types."""

    def test_cast_generic_with_no_handler_returns_as_is(self):
        """Test casting generic without handler returns value."""
        # Mapping has no handler but dict is instance of Mapping
        value = {"key": "value"}
        hint = Mapping[str, str]

        result = cast_value(value, hint)
        assert result == {"key": "value"}

    def test_cast_list_already_correct_type(self):
        """Test casting list that's already correct returns it."""
        value = [1, 2, 3]
        hint = List[int]

        result = cast_value(value, hint)
        assert result == [1, 2, 3]

    def test_cast_unknown_origin_not_iterable_raises_error(self):
        """Test casting unknown non-iterable origin raises error."""

        class NonIterableOrigin:
            pass

        value = "test"
        hint = NonIterableOrigin
        origin = NonIterableOrigin

        with pytest.raises(TypeError) as exc_info:
            cast_with_origin(value, hint, origin)

        assert "No casting handler" in str(exc_info.value)


class TestIntegrationCasting:
    """Test casting in real Classno usage."""

    def test_lossy_autocast_during_setattr(self):
        """Test autocast works when setting attributes."""

        class AutoCastClass(Classno):
            __features__ = Features.LOSSY_AUTOCAST
            age: int
            count: float

        obj = AutoCastClass(age=25, count=3.14)

        # Cast during setattr
        obj.age = "30"
        assert obj.age == 30
        assert isinstance(obj.age, int)

        obj.count = "2.5"
        assert obj.count == 2.5

    def test_union_with_none_and_complex_types(self):
        """Test casting union with None and complex types."""

        class TestClass(Classno):
            __features__ = Features.LOSSY_AUTOCAST
            data: Union[list[int], None, str]

        obj = TestClass(data="test")
        assert obj.data == "test"

        obj2 = TestClass(data=None)
        assert obj2.data is None

    def test_cast_union_skip_none_type_when_not_none(self):
        """Test union casting skips None when value is not None."""
        value = 42
        hint = Union[int, None]

        result = cast_union(value, hint)
        assert result == 42
