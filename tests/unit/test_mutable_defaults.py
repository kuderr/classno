"""
Tests for mutable default value validation.

These tests ensure that classno prevents shared mutable defaults
which can cause unexpected behavior between instances.
"""

import pytest
from typing import List, Dict, Set

from classno import Classno, field
from classno import Features


class TestMutableDefaultValidation:
    """Test validation of mutable default values."""

    def test_list_default_raises_error(self):
        """Test that using a list as default raises ValueError."""
        with pytest.raises(ValueError, match="Mutable default values are not allowed"):
            class TestClass(Classno):
                __features__ = Features.EQ
                items: List[str] = []

    def test_dict_default_raises_error(self):
        """Test that using a dict as default raises ValueError."""
        with pytest.raises(ValueError, match="Mutable default values are not allowed"):
            class TestClass(Classno):
                __features__ = Features.EQ
                mapping: Dict[str, int] = {}

    def test_set_default_raises_error(self):
        """Test that using a set as default raises ValueError."""
        with pytest.raises(ValueError, match="Mutable default values are not allowed"):
            class TestClass(Classno):
                __features__ = Features.EQ
                items: Set[str] = set()

    def test_bytearray_default_raises_error(self):
        """Test that using a bytearray as default raises ValueError."""
        with pytest.raises(ValueError, match="Mutable default values are not allowed"):
            class TestClass(Classno):
                __features__ = Features.EQ
                data: bytearray = bytearray(b'test')

    def test_field_list_default_raises_error(self):
        """Test that using field() with list default raises ValueError."""
        with pytest.raises(ValueError, match="Mutable default values are not allowed"):
            class TestClass(Classno):
                __features__ = Features.EQ
                items: List[str] = field(default=[])

    def test_field_dict_default_raises_error(self):
        """Test that using field() with dict default raises ValueError."""
        with pytest.raises(ValueError, match="Mutable default values are not allowed"):
            class TestClass(Classno):
                __features__ = Features.EQ
                mapping: Dict[str, int] = field(default={})

    def test_immutable_defaults_allowed(self):
        """Test that immutable defaults are still allowed."""
        class TestClass(Classno):
            __features__ = Features.EQ
            name: str = "default"
            count: int = 0
            enabled: bool = True
            value: float = 3.14
            data: tuple = (1, 2, 3)
            text: str = field(default="test")

        # Should create successfully
        obj1 = TestClass()
        obj2 = TestClass()
        
        # Verify defaults work
        assert obj1.name == "default"
        assert obj1.count == 0
        assert obj1.enabled is True
        assert obj1.value == 3.14
        assert obj1.data == (1, 2, 3)
        assert obj1.text == "test"

    def test_default_factory_list_works(self):
        """Test that using default_factory with list works correctly."""
        class TestClass(Classno):
            __features__ = Features.EQ
            items: List[str] = field(default_factory=list)

        obj1 = TestClass()
        obj2 = TestClass()
        
        # Verify each instance has its own list
        obj1.items.append("item1")
        assert obj1.items == ["item1"]
        assert obj2.items == []  # Should not be affected

    def test_default_factory_dict_works(self):
        """Test that using default_factory with dict works correctly."""
        class TestClass(Classno):
            __features__ = Features.EQ
            mapping: Dict[str, int] = field(default_factory=dict)

        obj1 = TestClass()
        obj2 = TestClass()
        
        # Verify each instance has its own dict
        obj1.mapping["key"] = 42
        assert obj1.mapping == {"key": 42}
        assert obj2.mapping == {}  # Should not be affected

    def test_default_factory_set_works(self):
        """Test that using default_factory with set works correctly."""
        class TestClass(Classno):
            __features__ = Features.EQ
            items: Set[str] = field(default_factory=set)

        obj1 = TestClass()
        obj2 = TestClass()
        
        # Verify each instance has its own set
        obj1.items.add("item1")
        assert obj1.items == {"item1"}
        assert obj2.items == set()  # Should not be affected

    def test_default_factory_lambda_works(self):
        """Test that using default_factory with lambda works correctly."""
        class TestClass(Classno):
            __features__ = Features.EQ
            items: List[str] = field(default_factory=lambda: ["default"])
            scores: Dict[str, int] = field(default_factory=lambda: {"start": 0})

        obj1 = TestClass()
        obj2 = TestClass()
        
        # Verify each instance has its own objects with default values
        obj1.items.append("item1")
        obj1.scores["level1"] = 100
        
        assert obj1.items == ["default", "item1"]
        assert obj1.scores == {"start": 0, "level1": 100}
        assert obj2.items == ["default"]  # Should not be affected
        assert obj2.scores == {"start": 0}  # Should not be affected

    def test_error_message_provides_solution(self):
        """Test that error message provides helpful solution."""
        with pytest.raises(ValueError) as exc_info:
            class TestClass(Classno):
                __features__ = Features.EQ
                items: List[str] = ["a", "b"]

        error_msg = str(exc_info.value)
        assert "Mutable default values are not allowed" in error_msg
        assert "default_factory=lambda: ['a', 'b']" in error_msg
        assert "to avoid shared state issues" in error_msg

    def test_none_default_allowed(self):
        """Test that None defaults are allowed (None is immutable)."""
        class TestClass(Classno):
            __features__ = Features.EQ
            optional_value: str = None

        obj = TestClass()
        assert obj.optional_value is None

    def test_custom_immutable_class_allowed(self):
        """Test that custom immutable classes as defaults are allowed."""
        class ImmutableClass:
            def __init__(self, value):
                self._value = value

        instance = ImmutableClass(42)

        class TestClass(Classno):
            __features__ = Features.EQ
            data: ImmutableClass = instance

        obj1 = TestClass()
        obj2 = TestClass()
        
        # Both should reference the same immutable object
        assert obj1.data is obj2.data
        assert obj1.data._value == 42