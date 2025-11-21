"""Tests for hashing functionality and edge cases."""

from classno import Classno
from classno import Features


class TestHashingBasics:
    """Test basic hashing functionality."""

    def test_hash_with_simple_fields(self):
        """Test hashing with simple field types."""

        class HashableClass(Classno):
            __features__ = Features.HASH
            name: str
            value: int

        obj = HashableClass(name="test", value=42)
        hash_value = hash(obj)

        assert isinstance(hash_value, int)

    def test_hash_consistency(self):
        """Test hash is consistent across calls."""

        class HashableClass(Classno):
            __features__ = Features.HASH
            name: str
            value: int

        obj = HashableClass(name="test", value=42)
        hash1 = hash(obj)
        hash2 = hash(obj)

        assert hash1 == hash2

    def test_hash_equal_objects_same_hash(self):
        """Test equal objects have same hash."""

        class HashableClass(Classno):
            __features__ = Features.HASH | Features.EQ
            name: str
            value: int

        obj1 = HashableClass(name="test", value=42)
        obj2 = HashableClass(name="test", value=42)

        assert obj1 == obj2
        assert hash(obj1) == hash(obj2)


class TestHashingWithUnhashableTypes:
    """Test hashing with normally unhashable types."""

    def test_hash_with_list_fields(self):
        """Test hashing objects with list fields."""

        class WithList(Classno):
            __features__ = Features.HASH
            items: list

        obj = WithList(items=[1, 2, 3])
        hash_value = hash(obj)

        # List is converted to hashable tuple internally
        assert isinstance(hash_value, int)

    def test_hash_with_dict_fields(self):
        """Test hashing objects with dict fields."""

        class WithDict(Classno):
            __features__ = Features.HASH
            data: dict

        obj = WithDict(data={"key": "value"})
        hash_value = hash(obj)

        assert isinstance(hash_value, int)

    def test_hash_with_set_fields(self):
        """Test hashing objects with set fields."""

        class WithSet(Classno):
            __features__ = Features.HASH
            items: set

        obj = WithSet(items={1, 2, 3})
        hash_value = hash(obj)

        assert isinstance(hash_value, int)


class TestHashingEdgeCases:
    """Test hashing edge cases."""

    def test_hash_with_unhashable_iterable_fallback(self):
        """Test unhashable iterables fall back to string representation."""

        class CustomIterable:
            """Custom iterable that raises TypeError when converting."""

            def __iter__(self):
                raise TypeError("Cannot iterate")

        class TestClass(Classno):
            __features__ = Features.HASH | Features.EQ
            data: object

        obj = TestClass(data=CustomIterable())

        # Should be hashable despite problematic iterable
        # Falls back to str() representation
        hash_value = hash(obj)
        assert isinstance(hash_value, int)

    def test_hash_with_nested_collections(self):
        """Test hashing with nested collection structures."""

        class NestedCollections(Classno):
            __features__ = Features.HASH
            nested: list

        obj = NestedCollections(nested=[[1, 2], [3, 4]])
        hash_value = hash(obj)

        assert isinstance(hash_value, int)

    def test_hash_usable_in_sets(self):
        """Test hashed objects can be used in sets."""

        class HashableClass(Classno):
            __features__ = Features.HASH | Features.EQ
            name: str
            value: int

        obj1 = HashableClass(name="test", value=42)
        obj2 = HashableClass(name="test", value=42)
        obj3 = HashableClass(name="other", value=99)

        obj_set = {obj1, obj2, obj3}

        # obj1 and obj2 have same hash, should be considered duplicate
        assert len(obj_set) == 2

    def test_hash_usable_as_dict_keys(self):
        """Test hashed objects can be used as dict keys."""

        class HashableClass(Classno):
            __features__ = Features.HASH | Features.EQ
            name: str

        obj1 = HashableClass(name="key1")
        obj2 = HashableClass(name="key1")  # Equal to obj1

        obj_dict = {obj1: "value1"}

        # obj2 is equal to obj1, should access same dict entry
        assert obj_dict[obj2] == "value1"
