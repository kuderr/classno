"""Tests for frozen feature functionality."""

import pytest

from classno import Classno
from classno import Features


class TestFrozenModification:
    """Test that frozen objects cannot be modified."""

    def test_frozen_prevents_attribute_modification(self):
        """Test frozen feature prevents modifying attributes."""

        class FrozenClass(Classno):
            __features__ = Features.FROZEN
            name: str

        obj = FrozenClass(name="test")

        with pytest.raises(AttributeError) as exc_info:
            obj.name = "changed"

        assert "Cannot modify" in str(exc_info.value)
        assert "frozen" in str(exc_info.value).lower()

    def test_frozen_prevents_attribute_deletion(self):
        """Test frozen feature prevents deleting attributes."""

        class FrozenClass(Classno):
            __features__ = Features.FROZEN
            name: str

        obj = FrozenClass(name="test")

        with pytest.raises(AttributeError) as exc_info:
            del obj.name

        assert "Cannot delete attributes" in str(exc_info.value)
        assert "FrozenClass" in str(exc_info.value)

    def test_frozen_with_multiple_fields(self):
        """Test frozen works with multiple fields."""

        class FrozenMultiple(Classno):
            __features__ = Features.FROZEN
            name: str
            age: int
            active: bool

        obj = FrozenMultiple(name="test", age=25, active=True)

        # All fields should be immutable
        with pytest.raises(AttributeError):
            obj.name = "new"
        with pytest.raises(AttributeError):
            obj.age = 30
        with pytest.raises(AttributeError):
            obj.active = False


class TestFrozenWithOtherFeatures:
    """Test frozen feature combined with other features."""

    def test_frozen_with_validation(self):
        """Test frozen and validation work together."""

        class FrozenValidated(Classno):
            __features__ = Features.FROZEN | Features.VALIDATION
            age: int

        # Can create valid object
        obj = FrozenValidated(age=25)
        assert obj.age == 25

        # Cannot modify
        with pytest.raises(AttributeError):
            obj.age = 30

    def test_frozen_with_hash(self):
        """Test frozen objects are hashable."""

        class FrozenHashable(Classno):
            __features__ = Features.FROZEN | Features.HASH
            name: str
            value: int

        obj1 = FrozenHashable(name="test", value=42)
        obj2 = FrozenHashable(name="test", value=42)

        # Should be hashable
        hash1 = hash(obj1)
        hash2 = hash(obj2)
        assert isinstance(hash1, int)
        assert hash1 == hash2

        # Can use in sets
        obj_set = {obj1, obj2}
        assert len(obj_set) == 1  # Same hash, considered duplicate
