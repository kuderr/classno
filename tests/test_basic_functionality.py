import pytest
from typing import Optional, Union, List, Dict, Tuple
from datetime import datetime

import classno
from classno import Classno, Features, field, MISSING


class TestBasicClassnoFunctionality:
    """Test basic Classno functionality including creation, default values, and field configuration."""

    def test_simple_class_creation(self):
        """Test creating a simple Classno class with basic fields."""
        class User(Classno):
            name: str
            age: int = 0
            email: str = field(default="")

        user = User(name="John", age=30)
        assert user.name == "John"
        assert user.age == 30
        assert user.email == ""

    def test_field_with_default_factory(self):
        """Test field with default_factory."""
        class Post(Classno):
            title: str
            content: str = ""
            created_at: datetime = field(default_factory=datetime.now)
            tags: list = field(default_factory=list)

        post = Post(title="Test Post")
        assert post.title == "Test Post"
        assert post.content == ""
        assert isinstance(post.created_at, datetime)
        assert post.tags == []

    def test_field_metadata(self):
        """Test field metadata configuration."""
        class Model(Classno):
            name: str = field(metadata={"indexed": True, "required": True})
            description: str = field(default="", metadata={"max_length": 255})

        model = Model(name="test")
        assert model.name == "test"
        assert model.description == ""

    def test_missing_required_field_raises_error(self):
        """Test that missing required fields raise appropriate errors."""
        class User(Classno):
            name: str
            email: str

        with pytest.raises(TypeError):
            User(name="John")  # Missing email

    def test_optional_fields(self):
        """Test optional field handling."""
        class User(Classno):
            name: str
            email: Optional[str] = None
            age: Optional[int] = None

        user = User(name="John")
        assert user.name == "John"
        assert user.email is None
        assert user.age is None

        user2 = User(name="Jane", email="jane@example.com", age=25)
        assert user2.email == "jane@example.com"
        assert user2.age == 25

    def test_union_types(self):
        """Test Union type handling."""
        class FlexibleModel(Classno):
            value: Union[int, str]
            number: Union[int, float] = 0

        model1 = FlexibleModel(value=42)
        assert model1.value == 42
        assert model1.number == 0

        model2 = FlexibleModel(value="hello", number=3.14)
        assert model2.value == "hello"
        assert model2.number == 3.14

    def test_complex_types(self):
        """Test complex type annotations."""
        class ComplexModel(Classno):
            numbers: List[int] = field(default_factory=list)
            mapping: Dict[str, int] = field(default_factory=dict)
            coordinates: Tuple[float, float] = (0.0, 0.0)
            tags: List[str] = field(default_factory=list)

        model = ComplexModel()
        assert model.numbers == []
        assert model.mapping == {}
        assert model.coordinates == (0.0, 0.0)
        assert model.tags == []

        model2 = ComplexModel(
            numbers=[1, 2, 3],
            mapping={"a": 1, "b": 2},
            coordinates=(10.5, 20.3),
            tags=["python", "dataclass"]
        )
        assert model2.numbers == [1, 2, 3]
        assert model2.mapping == {"a": 1, "b": 2}
        assert model2.coordinates == (10.5, 20.3)
        assert model2.tags == ["python", "dataclass"]


class TestFeatureConfiguration:
    """Test different feature combinations."""

    def test_eq_feature(self):
        """Test equality comparison feature."""
        class Person(Classno):
            __features__ = Features.EQ
            name: str
            age: int

        person1 = Person(name="John", age=30)
        person2 = Person(name="John", age=30)
        person3 = Person(name="Jane", age=25)

        assert person1 == person2
        assert person1 != person3

    def test_hash_feature(self):
        """Test hash feature."""
        class HashableItem(Classno):
            __features__ = Features.HASH
            name: str
            value: int

        item1 = HashableItem(name="test", value=42)
        item2 = HashableItem(name="test", value=42)
        item3 = HashableItem(name="different", value=42)

        # Should be hashable
        item_set = {item1, item2, item3}
        assert len(item_set) == 2  # item1 and item2 should have same hash

    def test_order_feature(self):
        """Test ordering feature."""
        class OrderedItem(Classno):
            __features__ = Features.ORDER
            name: str
            value: int

        item1 = OrderedItem(name="a", value=1)
        item2 = OrderedItem(name="b", value=2)
        item3 = OrderedItem(name="c", value=3)

        assert item1 < item2 < item3
        assert item3 > item2 > item1

    def test_slots_feature(self):
        """Test slots feature for memory optimization."""
        class SlottedClass(Classno):
            __features__ = Features.SLOTS
            name: str
            value: int

        obj = SlottedClass(name="test", value=42)
        assert obj.name == "test"
        assert obj.value == 42
        assert hasattr(SlottedClass, '__slots__')

    def test_combined_features(self):
        """Test combining multiple features."""
        class CombinedFeatures(Classno):
            __features__ = Features.EQ | Features.HASH | Features.ORDER
            name: str
            priority: int = 0

        item1 = CombinedFeatures(name="apple", priority=1)
        item2 = CombinedFeatures(name="banana", priority=10)
        item3 = CombinedFeatures(name="apple", priority=1)

        # Test equality
        assert item1 == item3
        assert item1 != item2

        # Test ordering (alphabetical by name first, then by priority)
        assert item1 < item2  # "apple" < "banana"

        # Test hashing
        item_set = {item1, item2, item3}
        assert len(item_set) == 2

    def test_default_features(self):
        """Test default feature combination."""
        class DefaultClass(Classno):
            __features__ = Features.DEFAULT
            name: str
            value: int

        obj1 = DefaultClass(name="test", value=1)
        obj2 = DefaultClass(name="test", value=1)
        obj3 = DefaultClass(name="other", value=2)

        # Should have equality by default
        assert obj1 == obj2
        assert obj1 != obj3