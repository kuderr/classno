"""Tests for dunder methods and comparison operations."""

from classno import Classno
from classno import Features


class TestComparisonDunders:
    """Test comparison dunder methods."""

    def test_eq_with_different_types_returns_not_implemented(self):
        """Test __eq__ returns NotImplemented for different types."""

        class TestClass(Classno):
            __features__ = Features.EQ
            value: int

        obj = TestClass(value=42)

        # Compare with completely different type
        result = obj.__eq__("not a TestClass")
        assert result is NotImplemented

    def test_lt_with_different_types_returns_not_implemented(self):
        """Test __lt__ returns NotImplemented for different types."""

        class TestClass(Classno):
            __features__ = Features.ORDER
            value: int

        obj = TestClass(value=42)

        result = obj.__lt__("not a TestClass")
        assert result is NotImplemented

    def test_le_with_different_types_returns_not_implemented(self):
        """Test __le__ returns NotImplemented for different types."""

        class TestClass(Classno):
            __features__ = Features.ORDER
            value: int

        obj = TestClass(value=42)

        result = obj.__le__(100.5)
        assert result is NotImplemented

    def test_gt_with_different_types_returns_not_implemented(self):
        """Test __gt__ returns NotImplemented for different types."""

        class TestClass(Classno):
            __features__ = Features.ORDER
            value: int

        obj = TestClass(value=42)

        result = obj.__gt__([1, 2, 3])
        assert result is NotImplemented

    def test_ge_with_different_types_returns_not_implemented(self):
        """Test __ge__ returns NotImplemented for different types."""

        class TestClass(Classno):
            __features__ = Features.ORDER
            value: int

        obj = TestClass(value=42)

        result = obj.__ge__({"key": "value"})
        assert result is NotImplemented


class TestComparisonWithSameType:
    """Test comparisons work correctly with same type."""

    def test_eq_with_same_values(self):
        """Test equality with same values."""

        class TestClass(Classno):
            __features__ = Features.EQ
            value: int

        obj1 = TestClass(value=42)
        obj2 = TestClass(value=42)

        assert obj1 == obj2

    def test_eq_with_different_values(self):
        """Test equality with different values."""

        class TestClass(Classno):
            __features__ = Features.EQ
            value: int

        obj1 = TestClass(value=42)
        obj2 = TestClass(value=99)

        assert obj1 != obj2

    def test_ordering_operations(self):
        """Test ordering operations."""

        class TestClass(Classno):
            __features__ = Features.ORDER
            value: int

        obj1 = TestClass(value=10)
        obj2 = TestClass(value=20)
        obj3 = TestClass(value=10)

        assert obj1 < obj2
        assert obj1 <= obj2
        assert obj1 <= obj3
        assert obj2 > obj1
        assert obj2 >= obj1
        assert obj1 >= obj3
