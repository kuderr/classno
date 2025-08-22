#!/usr/bin/env python3
"""Tests for newly added functionality: ForwardRef, slots fixes, hash fixes, and inheritance fixes."""

from collections import defaultdict
from collections import deque
from typing import Dict
from typing import List
from typing import Optional
from typing import Set

import pytest

from classno import Classno
from classno import Features
from classno import field
from classno.exceptions import ValidationError


class TestForwardRefValidation:
    """Test ForwardRef validation functionality."""

    def test_forward_ref_self_reference(self):
        """Test ForwardRef validation with self-referential types."""
        class Node(Classno):
            __features__ = Features.VALIDATION
            name: str
            parent: Optional["Node"] = None
            children: List["Node"] = field(default_factory=list)

        # Should work with forward references
        root = Node(name="root")
        child = Node(name="child", parent=root)
        grandchild = Node(name="grandchild", parent=child)

        assert child.parent == root
        assert grandchild.parent == child
        assert root.parent is None

    def test_forward_ref_validation_failure(self):
        """Test that ForwardRef validation properly rejects wrong types."""
        class Employee(Classno):
            __features__ = Features.VALIDATION
            name: str
            manager: Optional["Employee"] = None

        # Should reject wrong types
        with pytest.raises(ValidationError):
            Employee(name="John", manager="not an Employee")

        with pytest.raises(ValidationError):
            Employee(name="John", manager=123)

    def test_forward_ref_in_collections(self):
        """Test ForwardRef validation within collections."""
        class Team(Classno):
            __features__ = Features.VALIDATION
            name: str
            members: List["Team"] = field(default_factory=list)
            partnerships: Dict[str, "Team"] = field(default_factory=dict)

        team1 = Team(name="Alpha")
        team2 = Team(name="Beta")

        # Should work with valid forward refs in collections
        team1.members = [team2]
        team1.partnerships = {"ally": team2}

        assert len(team1.members) == 1
        assert team1.members[0].name == "Beta"
        assert team1.partnerships["ally"].name == "Beta"


class TestSlotsEnhancements:
    """Test enhanced slots functionality."""

    def test_slots_removes_dict(self):
        """Test that slots properly removes __dict__ from instances."""
        class SlottedClass(Classno):
            __features__ = Features.SLOTS
            name: str
            value: int

        obj = SlottedClass(name="test", value=42)

        # Should have __slots__ but no __dict__
        assert hasattr(SlottedClass, '__slots__')
        assert not hasattr(obj, '__dict__')

        # Should still work normally
        assert obj.name == "test"
        assert obj.value == 42

    def test_slots_with_default_values(self):
        """Test slots with default values and field factories."""
        class SlottedWithDefaults(Classno):
            __features__ = Features.SLOTS
            name: str
            tags: List[str] = field(default_factory=list)
            count: int = 0
            active: bool = True

        obj = SlottedWithDefaults(name="test")

        # Should have __slots__ but no __dict__
        assert hasattr(SlottedWithDefaults, '__slots__')
        assert not hasattr(obj, '__dict__')

        # Defaults should work
        assert obj.name == "test"
        assert obj.tags == []
        assert obj.count == 0
        assert obj.active is True

        # Should be able to modify
        obj.tags.append("test-tag")
        assert obj.tags == ["test-tag"]

    def test_slots_with_inheritance(self):
        """Test slots with inheritance."""
        class BaseSlotted(Classno):
            __features__ = Features.SLOTS
            base_field: str

        class ChildSlotted(BaseSlotted):
            child_field: int

        obj = ChildSlotted(base_field="base", child_field=42)

        # Should have __slots__ including inherited fields
        assert hasattr(ChildSlotted, '__slots__')
        assert not hasattr(obj, '__dict__')

        # Should access all fields
        assert obj.base_field == "base"
        assert obj.child_field == 42

    def test_immutable_uses_slots_properly(self):
        """Test that IMMUTABLE feature properly uses slots without __dict__."""
        class ImmutableData(Classno):
            __features__ = Features.IMMUTABLE
            id: int
            name: str
            data: List[str] = field(default_factory=list)

        obj = ImmutableData(id=1, name="test", data=["a", "b"])

        # Should have slots without __dict__
        assert hasattr(ImmutableData, '__slots__')
        assert not hasattr(obj, '__dict__')

        # Should be frozen
        with pytest.raises(Exception):
            obj.name = "changed"

        # Should be hashable (with our fix for unhashable collections)
        hash_value = hash(obj)
        assert isinstance(hash_value, int)


class TestHashEnhancements:
    """Test enhanced hash functionality with unhashable types."""

    def test_hash_with_list_fields(self):
        """Test hashing objects with list fields."""
        class WithList(Classno):
            __features__ = Features.HASH
            name: str
            items: List[str] = field(default_factory=list)

        obj1 = WithList(name="test", items=["a", "b", "c"])
        obj2 = WithList(name="test", items=["a", "b", "c"])
        obj3 = WithList(name="test", items=["a", "b", "d"])

        # Should be hashable despite list field
        hash1 = hash(obj1)
        hash2 = hash(obj2)
        hash3 = hash(obj3)

        assert isinstance(hash1, int)
        assert hash1 == hash2  # Same content, same hash
        assert hash1 != hash3  # Different content, different hash

    def test_hash_with_dict_fields(self):
        """Test hashing objects with dict fields."""
        class WithDict(Classno):
            __features__ = Features.HASH
            name: str
            data: Dict[str, int] = field(default_factory=dict)

        obj1 = WithDict(name="test", data={"a": 1, "b": 2})
        obj2 = WithDict(name="test", data={"b": 2, "a": 1})  # Different order
        obj3 = WithDict(name="test", data={"a": 1, "c": 3})

        # Should be hashable despite dict field
        hash1 = hash(obj1)
        hash2 = hash(obj2)
        hash3 = hash(obj3)

        assert isinstance(hash1, int)
        assert hash1 == hash2  # Same content, same hash (order independent)
        assert hash1 != hash3  # Different content, different hash

    def test_hash_with_set_fields(self):
        """Test hashing objects with set fields."""
        class WithSet(Classno):
            __features__ = Features.HASH
            name: str
            tags: Set[str] = field(default_factory=set)

        obj1 = WithSet(name="test", tags={"a", "b", "c"})
        obj2 = WithSet(name="test", tags={"c", "b", "a"})  # Different order
        obj3 = WithSet(name="test", tags={"a", "b", "d"})

        # Should be hashable despite set field
        hash1 = hash(obj1)
        hash2 = hash(obj2)
        hash3 = hash(obj3)

        assert isinstance(hash1, int)
        assert hash1 == hash2  # Same content, same hash (order independent)
        assert hash1 != hash3  # Different content, different hash

    def test_hash_with_complex_collections(self):
        """Test hashing with complex collection types."""
        class ComplexCollections(Classno):
            __features__ = Features.HASH
            name: str
            deque_field: deque = field(default_factory=deque)
            defaultdict_field: defaultdict = field(default_factory=lambda: defaultdict(list))

        obj1 = ComplexCollections(
            name="test",
            deque_field=deque([1, 2, 3]),
            defaultdict_field=defaultdict(list, {"a": [1, 2]})
        )

        # Should be hashable despite complex collection fields
        hash_value = hash(obj1)
        assert isinstance(hash_value, int)


class TestInheritanceEnhancements:
    """Test enhanced field inheritance functionality."""

    def test_field_inheritance_from_multiple_levels(self):
        """Test field inheritance across multiple inheritance levels."""
        class GrandParent(Classno):
            grand_field: str

        class Parent(GrandParent):
            parent_field: int

        class Child(Parent):
            __features__ = Features.VALIDATION
            child_field: float

        # Should inherit fields from all levels
        child = Child(grand_field="grand", parent_field=42, child_field=3.14)

        assert child.grand_field == "grand"
        assert child.parent_field == 42
        assert child.child_field == 3.14

        # Should validate all inherited fields
        with pytest.raises(ValidationError):
            Child(grand_field=123, parent_field=42, child_field=3.14)  # wrong type for grand_field

    def test_field_inheritance_with_multiple_inheritance(self):
        """Test field inheritance with multiple inheritance (mixin pattern)."""
        class TimestampMixin(Classno):
            created_at: str = "2023-01-01"

        class VersionMixin(Classno):
            version: int = 1

        class Document(TimestampMixin, VersionMixin):
            __features__ = Features.VALIDATION
            title: str
            content: str

        # Should inherit fields from all mixins
        doc = Document(title="Test", content="Content")

        assert doc.title == "Test"
        assert doc.content == "Content"
        assert doc.created_at == "2023-01-01"
        assert doc.version == 1

        # Should validate all fields including inherited ones
        with pytest.raises(ValidationError):
            Document(title=123, content="Content")  # wrong type for title

    def test_field_override_in_inheritance(self):
        """Test field type override in inheritance."""
        class Base(Classno):
            value: int = 0

        class Child(Base):
            __features__ = Features.VALIDATION
            value: str = "default"  # Override with different type

        # Child should use its own field definition
        child = Child()
        assert child.value == "default"

        # Should validate with child's type
        child_valid = Child(value="string")
        assert child_valid.value == "string"

        with pytest.raises(ValidationError):
            Child(value=123)  # int not allowed in child

    def test_mro_field_resolution(self):
        """Test that field resolution follows Method Resolution Order correctly."""
        class A(Classno):
            field: str = "A"

        class B(A):
            field: str = "B"

        class C(A):
            field: str = "C"

        class D(B, C):  # Diamond inheritance
            pass

        # Should use B's definition (first in MRO after D)
        d = D()
        assert d.field == "B"
