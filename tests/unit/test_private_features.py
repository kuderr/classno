"""Tests for private field functionality."""

import pytest

from classno import Classno
from classno import Features


class TestPrivateFieldAccess:
    """Test private field access patterns."""

    def test_private_field_write_with_underscore(self):
        """Test private fields must be written with underscore prefix."""

        class PrivateClass(Classno):
            __features__ = Features.PRIVATE
            field: str

        obj = PrivateClass(field="test")

        # Can read via public name
        assert obj.field == "test"

        # Cannot write via public name
        with pytest.raises(AttributeError) as exc_info:
            obj.field = "new_value"

        assert "private" in str(exc_info.value).lower()

        # Can write via underscore prefix
        obj._field = "modified"
        assert obj._field == "modified"
        assert obj.field == "modified"  # Read still works

    def test_private_field_nonexistent(self):
        """Test error when accessing non-existent private field."""

        class PrivateClass(Classno):
            __features__ = Features.PRIVATE
            name: str

        obj = PrivateClass(name="test")

        with pytest.raises(AttributeError) as exc_info:
            obj._nonexistent = "value"

        assert "not found" in str(exc_info.value)

    def test_private_field_multiple_fields(self):
        """Test private feature with multiple fields."""

        class PrivateMultiple(Classno):
            __features__ = Features.PRIVATE
            name: str
            age: int

        obj = PrivateMultiple(name="John", age=30)

        # Read access works
        assert obj.name == "John"
        assert obj.age == 30

        # Write must use underscore
        obj._name = "Jane"
        obj._age = 25

        assert obj.name == "Jane"
        assert obj.age == 25


class TestPrivateWithOtherFeatures:
    """Test private feature combined with other features."""

    def test_private_with_validation(self):
        """Test private and validation work together."""

        class PrivateValidated(Classno):
            __features__ = Features.PRIVATE | Features.VALIDATION
            age: int

        obj = PrivateValidated(age=25)
        assert obj.age == 25

        # Write with underscore and validation
        obj._age = 30
        assert obj.age == 30

    def test_private_with_lossy_autocast(self):
        """Test private and autocast work together."""

        class PrivateAutoCast(Classno):
            __features__ = Features.PRIVATE | Features.LOSSY_AUTOCAST
            count: int

        obj = PrivateAutoCast(count=10)

        # Cast when writing with underscore
        obj._count = "20"
        assert obj.count == 20
        assert isinstance(obj.count, int)
