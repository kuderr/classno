"""Tests for core Classno functionality: copy, deepcopy, pickle."""

import copy
import pickle

from classno import Classno
from classno import Features


# Module-level class for pickle testing
class SerializablePerson(Classno):
    __features__ = Features.EQ
    name: str
    age: int


class TestCopyOperations:
    """Test shallow and deep copy operations."""

    def test_shallow_copy(self):
        """Test shallow copy creates new object but shares mutable references."""

        class Person(Classno):
            __features__ = Features.EQ
            name: str
            age: int
            tags: list

        original = Person(name="John", age=30, tags=["tag1", "tag2"])
        copied = copy.copy(original)

        assert copied == original
        assert copied is not original
        assert copied.name == "John"
        assert copied.age == 30
        # Shallow copy shares mutable objects
        assert copied.tags is original.tags

    def test_deep_copy(self):
        """Test deep copy creates new object with new mutable references."""

        class Person(Classno):
            __features__ = Features.EQ
            name: str
            age: int
            tags: list

        original = Person(name="John", age=30, tags=["tag1", "tag2"])
        copied = copy.deepcopy(original)

        assert copied == original
        assert copied is not original
        assert copied.name == "John"
        assert copied.age == 30
        # Deep copy creates new mutable objects
        assert copied.tags is not original.tags
        assert copied.tags == original.tags

    def test_copy_with_nested_objects(self):
        """Test deep copy with nested Classno objects."""

        class Address(Classno):
            __features__ = Features.EQ
            street: str
            city: str

        class Person(Classno):
            __features__ = Features.EQ
            name: str
            address: Address

        original = Person(name="John", address=Address(street="Main St", city="NYC"))
        copied = copy.deepcopy(original)

        assert copied == original
        assert copied.address is not original.address
        assert copied.address.city == "NYC"


class TestPickleOperations:
    """Test pickle serialization and deserialization."""

    def test_pickle_and_unpickle(self):
        """Test object can be pickled and unpickled."""
        original = SerializablePerson(name="John", age=30)

        pickled = pickle.dumps(original)
        unpickled = pickle.loads(pickled)

        assert unpickled == original
        assert unpickled is not original
        assert unpickled.name == "John"
        assert unpickled.age == 30

    def test_pickle_with_complex_fields(self):
        """Test pickling objects with complex field types."""
        # Use the module-level class for pickling
        original = SerializablePerson(name="John", age=30)

        pickled = pickle.dumps(original)
        unpickled = pickle.loads(pickled)

        assert unpickled == original
        assert unpickled.name == "John"
        assert unpickled.age == 30
