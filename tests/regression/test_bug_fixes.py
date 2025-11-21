"""
Regression tests for fixed bugs.

These tests prevent reintroduction of bugs that were previously fixed.
Each test corresponds to a specific bug from the bug fixing phases.
"""

import collections
from typing import Dict
from typing import List
from typing import Optional
from typing import Set
from typing import Tuple
from typing import Union

import pytest

from classno import Classno
from classno import Features
from classno import field


class TestPhase1BugFixes:
    """Regression tests for Phase 1 bug fixes."""

    def test_equality_comparison_bug_fix(self):
        """
        Regression test for Bug #1 - Equality comparison bug.

        Previously: obj1 == obj2 would return True even when values were different
        due to incorrect use of getattr(self, key)() instead of getattr(other, key)()
        in _dunders.py:55
        """

        class TestClass(Classno):
            __features__ = Features.EQ
            value: int

        obj1 = TestClass(value=1)
        obj2 = TestClass(value=2)

        # This should be False, not True
        assert obj1 != obj2
        assert not (obj1 == obj2)

        # Same values should be equal
        obj3 = TestClass(value=1)
        assert obj1 == obj3

    def test_optional_type_validation_bug_fix(self):
        """
        Regression test for Bug #2 - Optional type validation bug.

        Previously: Optional[str] = None would fail validation
        Fixed: Proper Union type validation logic handles None values correctly
        """

        class TestClass(Classno):
            __features__ = Features.VALIDATION | Features.EQ
            optional_string: Optional[str] = None
            optional_int: Optional[int] = None

        # These should not raise validation errors
        obj1 = TestClass()  # Using defaults
        assert obj1.optional_string is None
        assert obj1.optional_int is None

        obj2 = TestClass(optional_string=None, optional_int=None)  # Explicit None
        assert obj2.optional_string is None
        assert obj2.optional_int is None

        obj3 = TestClass(optional_string="valid", optional_int=42)  # Valid values
        assert obj3.optional_string == "valid"
        assert obj3.optional_int == 42

    def test_missing_collection_type_handlers_bug_fix(self):
        """
        Regression test for Bug #3 - Missing validation/casting handlers.

        Previously: frozenset, deque, etc. would raise KeyError
        Fixed: Added handlers for all common collection types
        """

        class TestClass(Classno):
            __features__ = Features.VALIDATION | Features.EQ
            frozenset_field: frozenset[str]
            deque_field: collections.deque[int]
            defaultdict_field: collections.defaultdict[str, int]
            ordered_dict_field: collections.OrderedDict[str, str]
            counter_field: collections.Counter[str]

        # These should not raise KeyError during validation
        obj = TestClass(
            frozenset_field=frozenset(["a", "b", "c"]),
            deque_field=collections.deque([1, 2, 3]),
            defaultdict_field=collections.defaultdict(int, {"a": 1, "b": 2}),
            ordered_dict_field=collections.OrderedDict([("x", "1"), ("y", "2")]),
            counter_field=collections.Counter(["a", "a", "b"]),
        )

        assert obj.frozenset_field == frozenset(["a", "b", "c"])
        assert list(obj.deque_field) == [1, 2, 3]
        assert dict(obj.defaultdict_field) == {"a": 1, "b": 2}

    def test_casting_with_collection_types_bug_fix(self):
        """
        Regression test for casting with new collection types.

        Previously: Casting to frozenset, deque, etc. would fail
        Fixed: Added casting handlers for these types
        """

        class TestClass(Classno):
            __features__ = Features.LOSSY_AUTOCAST | Features.EQ
            frozenset_field: frozenset[str]
            deque_field: collections.deque[int]

        # Should cast from other iterable types
        obj = TestClass(
            frozenset_field=["a", "b", "c"],  # List -> frozenset
            deque_field=[1, 2, 3],  # List -> deque
        )

        assert obj.frozenset_field == frozenset(["a", "b", "c"])
        assert list(obj.deque_field) == [1, 2, 3]
        assert isinstance(obj.deque_field, collections.deque)


class TestPhase2BugFixes:
    """Regression tests for Phase 2 bug fixes."""

    def test_mutable_defaults_bug_fix(self):
        """
        Regression test for Bug #4 - Shared mutable defaults.

        Previously: field: List[str] = [] would be shared between instances
        Fixed: Added validation that prevents mutable defaults, requires default_factory
        """
        # This should now raise an error instead of creating shared state
        with pytest.raises(ValueError, match="Mutable default values are not allowed"):

            class BadClass(Classno):
                __features__ = Features.EQ
                items: List[str] = []  # Should raise error

        with pytest.raises(ValueError, match="Mutable default values are not allowed"):

            class BadDictClass(Classno):
                __features__ = Features.EQ
                mapping: Dict[str, int] = {}  # Should raise error

        # The correct way should work
        class GoodClass(Classno):
            __features__ = Features.EQ
            items: List[str] = field(default_factory=list)
            mapping: Dict[str, int] = field(default_factory=dict)

        obj1 = GoodClass()
        obj2 = GoodClass()

        # Should have independent mutable objects
        obj1.items.append("test")
        obj1.mapping["key"] = 42

        assert obj2.items == []  # Should not be affected
        assert obj2.mapping == {}  # Should not be affected

    def test_tuple_keys_type_preservation_bug_fix(self):
        """
        Regression test for tuple keys type preservation.

        Previously: __eq_keys__, __order_keys__, __hash_keys__ were set[str]
        Fixed: Changed to tuple[str, ...] to preserve order
        """

        class TestClass(Classno):
            __features__ = Features.EQ | Features.ORDER | Features.HASH
            __eq_keys__ = ("id", "name")
            __order_keys__ = ("priority", "name")
            __hash_keys__ = ("id",)

            id: int
            name: str
            priority: int

        # Verify the keys are tuples and preserve order
        assert isinstance(TestClass.__eq_keys__, tuple)
        assert isinstance(TestClass.__order_keys__, tuple)
        assert isinstance(TestClass.__hash_keys__, tuple)

        # Verify functionality works correctly
        obj1 = TestClass(id=1, name="alice", priority=1)
        obj2 = TestClass(id=1, name="alice", priority=2)  # Different priority

        # Should be equal based on id and name only
        assert obj1 == obj2

        # Should be ordered by priority first, then name
        obj3 = TestClass(id=2, name="bob", priority=0)  # Lower priority
        assert obj3 < obj1  # priority 0 < priority 1

    def test_casting_return_values_bug_fix(self):
        """
        Regression test for Bug #5 - Casting implicit None returns.

        Previously: cast_value() could return None implicitly in some code paths
        Fixed: All code paths now have explicit returns or raise exceptions
        """
        from classno._casting import cast_value

        # Basic casting should work
        result = cast_value("42", int)
        assert result == 42
        assert result is not None

        # Union casting should work
        result = cast_value(None, Optional[str])
        assert result is None  # Explicit None is OK

        result = cast_value("test", Optional[str])
        assert result == "test"
        assert result is not None

        # Complex casting should work
        result = cast_value({1: 2, 3: 4}, Dict[str, str])
        assert result == {"1": "2", "3": "4"}
        assert result is not None

        # Error cases should raise exceptions, not return None
        with pytest.raises(TypeError):
            cast_value("not_a_number", int)

    def test_union_none_handling_bug_fix(self):
        """
        Regression test for Union None handling in casting.

        Previously: None values in Union types would be cast to strings like "None"
        Fixed: Special handling for None values in Union types
        """
        from classno._casting import cast_value

        # None should remain None in Optional types
        result = cast_value(None, Optional[str])
        assert result is None
        assert result != "None"  # Should not be the string "None"

        result = cast_value(None, Union[str, int, None])
        assert result is None

        # Non-None values should be handled normally
        result = cast_value("test", Optional[str])
        assert result == "test"

        result = cast_value(42, Union[str, int, None])
        assert result == 42

    def test_dict_casting_keys_and_values_bug_fix(self):
        """
        Regression test for dict casting bug.

        Previously: Dict casting only validated keys, didn't cast them
        Fixed: Dict casting now casts both keys and values
        """
        from classno._casting import cast_value

        # Keys and values should both be cast
        result = cast_value({1: 2, 3: 4}, Dict[str, str])
        assert result == {"1": "2", "3": "4"}

        # Verify types are correct
        for key, value in result.items():
            assert isinstance(key, str)
            assert isinstance(value, str)


class TestComprehensiveRegressionScenarios:
    """Comprehensive scenarios that test multiple bug fixes together."""

    def test_complex_scenario_with_all_fixes(self):
        """Test a complex scenario using all the fixed functionality."""

        class ComplexClass(Classno):
            __features__ = (
                Features.EQ
                | Features.ORDER
                | Features.VALIDATION
                | Features.LOSSY_AUTOCAST
            )
            __eq_keys__ = ("id",)  # Tuple type
            __order_keys__ = ("priority", "name")  # Tuple type

            id: int
            name: str
            priority: int
            optional_data: Optional[Dict[str, List[str]]] = None
            items: frozenset[str] = field(
                default_factory=frozenset
            )  # No mutable defaults
            metadata: collections.deque[int] = field(default_factory=collections.deque)

        # Should work with casting and validation
        obj1 = ComplexClass(
            id="1",  # Will be cast to int
            name="test",
            priority="5",  # Will be cast to int
            optional_data={"group": ["a", "b"]},
            items=["x", "y", "z"],  # Will be cast to frozenset
            metadata=["1", "2", "3"],  # Will be cast to deque of ints
        )

        assert obj1.id == 1
        assert obj1.priority == 5
        assert obj1.optional_data == {"group": ["a", "b"]}
        assert obj1.items == frozenset(["x", "y", "z"])
        assert list(obj1.metadata) == [1, 2, 3]

        # Test equality (uses fixed comparison)
        obj2 = ComplexClass(
            id=1,  # Same id
            name="different",  # Different name
            priority=10,  # Different priority
            optional_data=None,  # Different optional data
        )

        # Should be equal based on id only
        assert obj1 == obj2

        # Test ordering (uses tuple keys)
        obj3 = ComplexClass(id=2, name="alice", priority=1)  # Lower priority
        assert obj3 < obj1  # Lower priority sorts first

        # Test independent default objects (no shared mutable state)
        obj4 = ComplexClass(id=3, name="test", priority=1)
        obj5 = ComplexClass(id=4, name="test", priority=1)

        # Modify mutable fields
        obj4.metadata.append(100)

        # obj5 should not be affected
        assert list(obj5.metadata) == []

    def test_inheritance_with_all_fixes(self):
        """Test inheritance scenarios with all bug fixes."""

        class BaseClass(Classno):
            __features__ = Features.EQ | Features.VALIDATION
            __eq_keys__ = ("id",)  # Tuple type

            id: int
            base_optional: Optional[str] = None
            base_collection: Set[str] = field(
                default_factory=set
            )  # No mutable defaults

        class ExtendedClass(BaseClass):
            __features__ = Features.EQ | Features.VALIDATION | Features.LOSSY_AUTOCAST
            __eq_keys__ = ("id", "version")  # Override with tuple

            version: int
            extended_optional: Optional[List[int]] = None
            extended_collection: frozenset[int] = field(default_factory=frozenset)

        # Should work with all features
        obj = ExtendedClass(
            id="1",  # Cast to int
            base_optional=None,  # Optional handling
            version="2",  # Cast to int
            extended_optional=[1, 2, 3],
            extended_collection=[4, 5, 6],  # Cast to frozenset
        )

        assert obj.id == 1
        assert obj.version == 2
        assert obj.base_optional is None
        assert obj.extended_optional == [1, 2, 3]
        assert obj.extended_collection == frozenset([4, 5, 6])

    def test_edge_case_combinations(self):
        """Test edge case combinations that previously might have failed."""

        class EdgeCaseClass(Classno):
            __features__ = Features.EQ | Features.VALIDATION | Features.LOSSY_AUTOCAST

            # Complex Union with Optional
            complex_union: Union[str, List[int], None] = None

            # Nested Optional structures
            nested_optional: Optional[Dict[str, Optional[List[str]]]] = None

            # Collections that previously had no handlers
            special_collections: Tuple[frozenset[str], collections.deque[int]] = field(
                default_factory=lambda: (frozenset(), collections.deque())
            )

        obj = EdgeCaseClass(
            complex_union=[1, 2, 3],  # List[int] from union
            nested_optional={"group": ["a", "b"], "empty": None},
            special_collections=(["x", "y"], [10, 20]),  # Will be cast appropriately
        )

        assert obj.complex_union == [1, 2, 3]
        assert obj.nested_optional["group"] == ["a", "b"]
        assert obj.nested_optional["empty"] is None
        assert obj.special_collections[0] == frozenset(["x", "y"])
        assert list(obj.special_collections[1]) == [10, 20]
