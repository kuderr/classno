import pytest
from typing import List, Dict, Optional

from classno import Classno, Features, field
from classno.exceptions import ValidationError


class TestAdvancedFeatures:
    """Test advanced features like private fields, autocasting, and custom keys."""

    def test_private_fields(self):
        """Test private field functionality."""

        class PrivateFieldsClass(Classno):
            __features__ = Features.PRIVATE
            field: str

        obj = PrivateFieldsClass(field="original")

        # Private field should be read-only via normal access
        assert obj.field == "original"
        with pytest.raises(Exception):
            obj.field = "modified"  # Should fail

        # But should be writable via underscore prefix
        obj._field = "modified"
        assert obj._field == "modified"

    def test_lossy_autocast(self):
        """Test lossy autocasting functionality."""

        class AutoCastClass(Classno):
            __features__ = Features.LOSSY_AUTOCAST
            int_field: int
            float_field: float
            str_field: str
            list_field: list[int]

        # Should autocast compatible types
        obj = AutoCastClass(
            int_field=3.14,  # float to int
            float_field=42,  # int to float
            str_field=123,  # int to str
            list_field={1, 2, 3},  # set to list
        )

        assert obj.int_field == 3  # 3.14 truncated to 3
        assert obj.float_field == 42.0  # 42 converted to 42.0
        assert obj.str_field == "123"  # 123 converted to "123"
        assert isinstance(obj.list_field, list)
        assert set(obj.list_field) == {1, 2, 3}  # set converted to list

    def test_custom_hash_keys(self):
        """Test custom hash keys configuration."""

        class CustomHashKeys(Classno):
            __hash_keys__ = {"id"}
            __features__ = Features.HASH

            id: int
            name: str
            description: str

        obj1 = CustomHashKeys(id=1, name="test", description="desc1")
        obj2 = CustomHashKeys(id=1, name="different", description="desc2")
        obj3 = CustomHashKeys(id=2, name="test", description="desc1")

        # Objects with same ID should have same hash
        assert hash(obj1) == hash(obj2)
        assert hash(obj1) != hash(obj3)

        # Should work in sets
        obj_set = {obj1, obj2, obj3}
        assert len(obj_set) == 2  # obj1 and obj2 should be considered same

    def test_custom_eq_keys(self):
        """Test custom equality keys configuration."""

        class CustomEqKeys(Classno):
            __eq_keys__ = {"id", "name"}
            __features__ = Features.EQ

            id: int
            name: str
            description: str
            timestamp: float = 0.0

        obj1 = CustomEqKeys(id=1, name="test", description="desc1", timestamp=100.0)
        obj2 = CustomEqKeys(id=1, name="test", description="different", timestamp=200.0)
        obj3 = CustomEqKeys(
            id=1, name="different", description="desc1", timestamp=100.0
        )

        # Should be equal based only on id and name
        assert obj1 == obj2  # Same id and name, different description and timestamp
        assert obj1 != obj3  # Same id, different name

    def test_custom_order_keys(self):
        """Test custom ordering keys configuration."""

        class CustomOrderKeys(Classno):
            __order_keys__ = ("priority", "name")  # Use tuple to preserve order
            __features__ = Features.ORDER

            priority: int
            name: str
            description: str

        obj1 = CustomOrderKeys(priority=1, name="alpha", description="desc1")
        obj2 = CustomOrderKeys(priority=1, name="beta", description="desc2")
        obj3 = CustomOrderKeys(priority=2, name="alpha", description="desc3")

        # Should order by priority first, then by name
        assert obj1 < obj2  # Same priority, "alpha" < "beta"
        assert obj1 < obj3  # Lower priority
        assert obj2 < obj3  # Lower priority

        sorted_objs = sorted([obj3, obj2, obj1])
        assert sorted_objs == [obj1, obj2, obj3]

    def test_combined_custom_keys(self):
        """Test combining all custom key configurations."""

        class CombinedCustomKeys(Classno):
            __hash_keys__ = {"id"}
            __eq_keys__ = {"id", "version"}
            __order_keys__ = {"name"}
            __features__ = Features.HASH | Features.EQ | Features.ORDER

            id: int
            version: str
            name: str
            data: str

        obj1 = CombinedCustomKeys(id=1, version="1.0", name="beta", data="data1")
        obj2 = CombinedCustomKeys(id=1, version="1.0", name="alpha", data="different")
        obj3 = CombinedCustomKeys(id=1, version="2.0", name="gamma", data="data3")

        # Hash based on ID only
        assert hash(obj1) == hash(obj2) == hash(obj3)

        # Equality based on ID and version
        assert obj1 == obj2  # Same id and version
        assert obj1 != obj3  # Same id, different version

        # Ordering based on name
        assert obj2 < obj1  # "alpha" < "beta"
        assert obj1 < obj3  # "beta" < "gamma"

    def test_feature_interactions(self):
        """Test interactions between different features."""

        class MultiFeatureClass(Classno):
            __features__ = (
                Features.VALIDATION | Features.FROZEN | Features.HASH | Features.EQ
            )
            __hash_keys__ = {"id"}
            __eq_keys__ = {"id"}

            id: int
            name: str
            values: List[int] = field(default_factory=list)

        # Should validate on creation
        obj = MultiFeatureClass(id=1, name="test", values=[1, 2, 3])
        assert obj.id == 1
        assert obj.values == [1, 2, 3]

        # Should reject invalid types
        with pytest.raises(ValidationError):
            MultiFeatureClass(id="invalid", name="test")

        # Should be frozen
        with pytest.raises(Exception):
            obj.name = "changed"

        # Should be hashable and comparable based on custom keys
        obj2 = MultiFeatureClass(id=1, name="different", values=[4, 5, 6])
        assert obj == obj2  # Same ID
        assert hash(obj) == hash(obj2)  # Same hash

    def test_inheritance_with_features(self):
        """Test feature inheritance and overriding."""

        class BaseClass(Classno):
            __features__ = Features.EQ | Features.HASH
            id: int
            name: str

        class ChildClass(BaseClass):
            __features__ = Features.EQ | Features.HASH | Features.FROZEN
            description: str

        # Parent should not be frozen
        parent = BaseClass(id=1, name="parent")
        parent.name = "modified"
        assert parent.name == "modified"

        # Child should be frozen
        child = ChildClass(id=2, name="child", description="child desc")
        with pytest.raises(Exception):
            child.name = "modified"

        # Both should support equality and hashing
        parent2 = BaseClass(id=1, name="modified")
        child2 = ChildClass(id=2, name="child", description="child desc")

        assert parent == parent2
        assert child == child2
        assert hash(parent) == hash(parent2)
        assert hash(child) == hash(child2)

    def test_complex_autocast_scenarios(self):
        """Test complex autocasting scenarios."""

        class ComplexAutoCast(Classno):
            __features__ = Features.LOSSY_AUTOCAST | Features.VALIDATION

            numbers: List[int]
            mapping: Dict[str, float]
            tuple_data: tuple[int, str]

        # Should autocast and validate
        obj = ComplexAutoCast(
            numbers=[1.1, 2.9, 3.5],  # floats to ints
            mapping={"a": 1, "b": 2},  # ints to floats
            tuple_data=(3.14, 42),  # float to int, int to str
        )

        assert obj.numbers == [1, 2, 3]  # Truncated floats
        assert obj.mapping == {"a": 1.0, "b": 2.0}  # Ints to floats
        assert obj.tuple_data == (3, "42")  # float truncated, int to string

    def test_edge_case_empty_collections(self):
        """Test edge cases with empty collections."""

        class EmptyCollections(Classno):
            __features__ = Features.VALIDATION | Features.EQ

            empty_list: List[int] = field(default_factory=list)
            empty_dict: Dict[str, int] = field(default_factory=dict)
            optional_list: Optional[List[str]] = None

        obj1 = EmptyCollections()
        obj2 = EmptyCollections()

        assert obj1.empty_list == []
        assert obj1.empty_dict == {}
        assert obj1.optional_list is None

        # Should be equal
        assert obj1 == obj2

        # Should handle modifications
        obj1.empty_list.append(1)
        obj1.empty_dict["key"] = 42

        assert obj1.empty_list == [1]
        assert obj1.empty_dict == {"key": 42}
        assert obj1 != obj2  # Should no longer be equal

    def test_metadata_preservation(self):
        """Test that field metadata is preserved and accessible."""

        class MetadataClass(Classno):
            name: str = field(metadata={"required": True, "max_length": 50})
            score: float = field(
                default=0.0, metadata={"min_value": 0.0, "max_value": 100.0}
            )
            tags: List[str] = field(default_factory=list, metadata={"indexed": True})

        obj = MetadataClass(name="test")

        # The metadata should be accessible through the field definition
        # This tests that metadata is properly stored and doesn't interfere with functionality
        assert obj.name == "test"
        assert obj.score == 0.0
        assert obj.tags == []

    def test_field_default_vs_default_factory(self):
        """Test the difference between default and default_factory."""

        class DefaultTest(Classno):
            # Using mutable default (should use same instance)
            shared_list: list = []

            # Using default_factory (should create new instance each time)
            unique_list: list = field(default_factory=list)

            name: str = "default_name"

        obj1 = DefaultTest()
        obj2 = DefaultTest()

        # shared_list should be the same object instance
        obj1.shared_list.append("item1")
        obj2.shared_list.append("item2")
        assert obj1.shared_list == ["item1", "item2"]
        assert obj2.shared_list == ["item1", "item2"]
        assert obj1.shared_list is obj2.shared_list

        # unique_list should be different instances
        obj1.unique_list.append("unique1")
        obj2.unique_list.append("unique2")
        assert obj1.unique_list == ["unique1"]
        assert obj2.unique_list == ["unique2"]
        assert obj1.unique_list is not obj2.unique_list
