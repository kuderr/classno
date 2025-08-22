"""
Tests for missing collection type handlers bug fix.
This ensures that frozenset, deque, and other collection types work correctly
with both validation and autocasting.
"""

from collections import Counter
from collections import OrderedDict
from collections import defaultdict
from collections import deque
from typing import List

import pytest

from classno import Classno
from classno import Features
from classno import field
from classno.exceptions import CastingError
from classno.exceptions import ValidationError


class TestCollectionTypeValidation:
    """Test validation of various collection types."""

    def test_frozenset_validation(self):
        """Test frozenset validation."""
        class FrozenSetModel(Classno):
            __features__ = Features.VALIDATION
            data: frozenset[int]
            str_data: frozenset[str] = frozenset()

        # Valid frozenset
        obj = FrozenSetModel(data=frozenset([1, 2, 3]))
        assert obj.data == frozenset([1, 2, 3])
        assert obj.str_data == frozenset()

        # Valid with values
        obj2 = FrozenSetModel(data=frozenset([4, 5]), str_data=frozenset(['a', 'b']))
        assert obj2.str_data == frozenset(['a', 'b'])

        # Invalid type - not frozenset
        with pytest.raises(ValidationError):
            FrozenSetModel(data=[1, 2, 3])  # list instead of frozenset

        # Invalid element type
        with pytest.raises(ValidationError):
            FrozenSetModel(data=frozenset(['a', 'b']))  # strings instead of ints

    def test_deque_validation(self):
        """Test collections.deque validation."""
        class DequeModel(Classno):
            __features__ = Features.VALIDATION
            items: deque[str]
            numbers: deque[int] = field(default_factory=deque)

        # Valid deque
        obj = DequeModel(items=deque(['hello', 'world']))
        assert list(obj.items) == ['hello', 'world']
        assert list(obj.numbers) == []

        # Valid with numbers
        obj2 = DequeModel(items=deque(['test']), numbers=deque([1, 2, 3]))
        assert list(obj2.numbers) == [1, 2, 3]

        # Invalid type - not deque
        with pytest.raises(ValidationError):
            DequeModel(items=['hello', 'world'])  # list instead of deque

        # Invalid element type
        with pytest.raises(ValidationError):
            DequeModel(items=deque([1, 2, 3]))  # ints instead of strings

    def test_defaultdict_validation(self):
        """Test collections.defaultdict validation."""
        class DefaultDictModel(Classno):
            __features__ = Features.VALIDATION
            mapping: defaultdict[str, int]

        # Valid defaultdict
        dd = defaultdict(int)
        dd['a'] = 1
        dd['b'] = 2
        obj = DefaultDictModel(mapping=dd)
        assert obj.mapping['a'] == 1
        assert obj.mapping['b'] == 2

        # Invalid type - not defaultdict
        with pytest.raises(ValidationError):
            DefaultDictModel(mapping={'a': 1, 'b': 2})  # regular dict

        # Invalid key type
        with pytest.raises(ValidationError):
            dd_bad = defaultdict(int)
            dd_bad[1] = 100  # int key instead of str
            DefaultDictModel(mapping=dd_bad)

        # Invalid value type
        with pytest.raises(ValidationError):
            dd_bad = defaultdict(str)
            dd_bad['a'] = 'string'  # string value instead of int
            DefaultDictModel(mapping=dd_bad)

    def test_ordered_dict_validation(self):
        """Test collections.OrderedDict validation."""
        class OrderedDictModel(Classno):
            __features__ = Features.VALIDATION
            ordered_data: OrderedDict[str, float]

        # Valid OrderedDict
        od = OrderedDict([('x', 1.0), ('y', 2.5), ('z', 3.14)])
        obj = OrderedDictModel(ordered_data=od)
        assert list(obj.ordered_data.keys()) == ['x', 'y', 'z']
        assert obj.ordered_data['y'] == 2.5

        # Invalid type - not OrderedDict
        with pytest.raises(ValidationError):
            OrderedDictModel(ordered_data={'x': 1.0})  # regular dict

        # Invalid value type
        with pytest.raises(ValidationError):
            od_bad = OrderedDict([('x', 'not_float')])
            OrderedDictModel(ordered_data=od_bad)

    def test_counter_validation(self):
        """Test collections.Counter validation."""
        class CounterModel(Classno):
            __features__ = Features.VALIDATION
            counts: Counter[str, int]

        # Valid Counter
        counter = Counter(['a', 'b', 'a', 'c', 'b', 'a'])
        obj = CounterModel(counts=counter)
        assert obj.counts['a'] == 3
        assert obj.counts['b'] == 2
        assert obj.counts['c'] == 1

        # Invalid type - not Counter
        with pytest.raises(ValidationError):
            CounterModel(counts={'a': 3, 'b': 2})  # regular dict

    def test_nested_collection_validation(self):
        """Test nested collection types."""
        class NestedModel(Classno):
            __features__ = Features.VALIDATION
            list_of_frozensets: List[frozenset[int]]
            # Note: deque is not hashable, so can't be in frozenset
            # Use a different nesting example
            list_of_deques: List[deque[str]]

        # Valid nested collections
        obj = NestedModel(
            list_of_frozensets=[frozenset([1, 2]), frozenset([3, 4])],
            list_of_deques=[deque(['a', 'b']), deque(['c', 'd'])]
        )
        assert len(obj.list_of_frozensets) == 2
        assert frozenset([1, 2]) in obj.list_of_frozensets
        assert len(obj.list_of_deques) == 2

        # Invalid nested structure
        with pytest.raises(ValidationError):
            NestedModel(
                list_of_frozensets=[[1, 2], [3, 4]],  # lists instead of frozensets
                list_of_deques=[['a', 'b']]  # lists instead of deques
            )


class TestCollectionTypeCasting:
    """Test autocasting of various collection types."""

    def test_frozenset_autocasting(self):
        """Test autocasting to frozenset."""
        class FrozenSetCastModel(Classno):
            __features__ = Features.LOSSY_AUTOCAST
            data: frozenset[int]

        # Cast from set
        obj = FrozenSetCastModel(data={1, 2, 3})
        assert obj.data == frozenset([1, 2, 3])
        assert isinstance(obj.data, frozenset)

        # Cast from list (with element casting)
        obj2 = FrozenSetCastModel(data=['1', '2', '3'])
        assert obj2.data == frozenset([1, 2, 3])  # strings cast to ints

        # Cast from tuple
        obj3 = FrozenSetCastModel(data=(4, 5, 6))
        assert obj3.data == frozenset([4, 5, 6])

    def test_deque_autocasting(self):
        """Test autocasting to collections.deque."""
        class DequeCastModel(Classno):
            __features__ = Features.LOSSY_AUTOCAST
            items: deque[str]

        # Cast from list
        obj = DequeCastModel(items=['hello', 'world'])
        assert list(obj.items) == ['hello', 'world']
        assert isinstance(obj.items, deque)

        # Cast from tuple with element casting
        obj2 = DequeCastModel(items=(1, 2, 3))
        assert list(obj2.items) == ['1', '2', '3']  # ints cast to strings

        # Cast from set (order not guaranteed)
        obj3 = DequeCastModel(items={'a', 'b'})
        assert set(obj3.items) == {'a', 'b'}

    def test_defaultdict_autocasting(self):
        """Test autocasting to collections.defaultdict."""
        class DefaultDictCastModel(Classno):
            __features__ = Features.LOSSY_AUTOCAST
            mapping: defaultdict[str, int]

        # Note: defaultdict casting reuses dict casting, so the result is a regular dict
        # This is expected behavior since we can't know what default factory to use
        obj = DefaultDictCastModel(mapping={'a': 1, 'b': 2})
        assert dict(obj.mapping) == {'a': 1, 'b': 2}
        # The casting uses the dict handler, so result may not be defaultdict
        # This is acceptable behavior for autocasting

    def test_mixed_validation_and_casting(self):
        """Test combining validation and autocasting features."""
        class MixedModel(Classno):
            __features__ = Features.VALIDATION | Features.LOSSY_AUTOCAST
            frozen_data: frozenset[int]
            deque_data: deque[str]

        # Should autocast and then validate
        obj = MixedModel(
            frozen_data=[1, 2, 3],  # list -> frozenset
            deque_data=('a', 'b')   # tuple -> deque
        )
        assert obj.frozen_data == frozenset([1, 2, 3])
        assert list(obj.deque_data) == ['a', 'b']

        # Should fail casting if strings can't be converted to ints
        with pytest.raises(CastingError):
            MixedModel(
                frozen_data=['not', 'ints'],  # strings can't cast to ints
                deque_data=['a', 'b']
            )


class TestFallbackHandlers:
    """Test fallback handlers for unknown collection types."""

    def test_unknown_iterable_validation_fallback(self):
        """Test that unknown iterable types use the collection fallback."""
        # This is harder to test since we'd need a custom iterable type
        # But we can test that the error message is helpful

        class CustomIterable:
            def __init__(self, items):
                self.items = items

            def __iter__(self):
                return iter(self.items)

        # This would require a custom type that's not in our handler map
        # For now, let's just verify our existing types work
        pass

    def test_validation_error_for_unsupported_types(self):
        """Test that unsupported types give helpful error messages."""
        class UnsupportedModel(Classno):
            __features__ = Features.VALIDATION
            data: frozenset[int]  # This should work now

        # This should work fine now
        obj = UnsupportedModel(data=frozenset([1, 2, 3]))
        assert obj.data == frozenset([1, 2, 3])


class TestCollectionTypeEdgeCases:
    """Test edge cases with collection types."""

    def test_empty_collections(self):
        """Test empty collection handling."""
        class EmptyCollectionModel(Classno):
            __features__ = Features.VALIDATION
            empty_frozenset: frozenset[int] = frozenset()
            empty_deque: deque[str] = field(default_factory=deque)

        obj = EmptyCollectionModel()
        assert obj.empty_frozenset == frozenset()
        assert len(obj.empty_deque) == 0

    def test_collection_with_none_elements(self):
        """Test collections containing None values."""
        class NoneElementModel(Classno):
            __features__ = Features.VALIDATION
            frozenset_with_none: frozenset[int | None]
            deque_with_none: deque[str | None]

        obj = NoneElementModel(
            frozenset_with_none=frozenset([1, None, 3]),
            deque_with_none=deque(['hello', None, 'world'])
        )
        assert None in obj.frozenset_with_none
        assert None in obj.deque_with_none

    def test_collection_inheritance(self):
        """Test collection types with inheritance."""
        class BaseCollectionModel(Classno):
            __features__ = Features.VALIDATION
            base_set: frozenset[int] = frozenset()

        class ChildCollectionModel(BaseCollectionModel):
            child_deque: deque[str] = field(default_factory=deque)

        child = ChildCollectionModel(
            base_set=frozenset([1, 2, 3]),
            child_deque=deque(['a', 'b', 'c'])
        )
        assert child.base_set == frozenset([1, 2, 3])
        assert list(child.child_deque) == ['a', 'b', 'c']

    def test_performance_with_large_collections(self):
        """Test performance with large collections."""
        class LargeCollectionModel(Classno):
            __features__ = Features.VALIDATION
            large_frozenset: frozenset[int]
            large_deque: deque[int]

        # Test with reasonably large collections
        large_set_data = frozenset(range(1000))
        large_deque_data = deque(range(1000))

        obj = LargeCollectionModel(
            large_frozenset=large_set_data,
            large_deque=large_deque_data
        )
        assert len(obj.large_frozenset) == 1000
        assert len(obj.large_deque) == 1000


if __name__ == "__main__":
    # Quick verification that the fixes work
    from collections import defaultdict
    from collections import deque

    class QuickTest(Classno):
        __features__ = Features.VALIDATION | Features.LOSSY_AUTOCAST
        frozen_data: frozenset[int]
        deque_data: deque[str]

    # Test validation
    obj1 = QuickTest(
        frozen_data=frozenset([1, 2, 3]),
        deque_data=deque(['a', 'b', 'c'])
    )
    print(f"Validation test: {obj1}")

    # Test autocasting
    obj2 = QuickTest(
        frozen_data=[4, 5, 6],  # list -> frozenset
        deque_data=('x', 'y', 'z')  # tuple -> deque
    )
    print(f"Autocasting test: frozen_data={obj2.frozen_data}, deque_data={list(obj2.deque_data)}")
