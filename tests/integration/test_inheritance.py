"""
Integration tests for inheritance scenarios.

Tests how classno classes work with inheritance, including
feature inheritance, field inheritance, and complex hierarchies.
"""

from typing import Dict
from typing import List
from typing import Optional
from typing import Union

import pytest

from classno import Classno
from classno import Features
from classno import field


class TestInheritanceScenarios:
    """Test various inheritance patterns with classno."""

    def test_basic_inheritance(self):
        """Test basic single inheritance."""
        class Animal(Classno):
            __features__ = Features.EQ | Features.REPR
            name: str
            age: int

        class Dog(Animal):
            breed: str

        dog = Dog(name="Buddy", age=5, breed="Golden Retriever")
        assert dog.name == "Buddy"
        assert dog.age == 5
        assert dog.breed == "Golden Retriever"

        # Should have features from parent
        assert repr(dog)  # REPR feature

        dog2 = Dog(name="Buddy", age=5, breed="Golden Retriever")
        assert dog == dog2  # EQ feature

    def test_feature_inheritance_and_extension(self):
        """Test inheriting and extending features."""
        class Base(Classno):
            __features__ = Features.EQ
            id: int
            name: str

        class Extended(Base):
            __features__ = Features.EQ | Features.ORDER | Features.HASH
            priority: int

        obj1 = Extended(id=1, name="first", priority=1)
        obj2 = Extended(id=2, name="second", priority=2)

        # Should have all features
        assert obj1 != obj2  # EQ
        assert obj1 < obj2   # ORDER
        assert hash(obj1) != hash(obj2)  # HASH

    def test_custom_keys_inheritance(self):
        """Test inheritance of custom keys."""
        class Base(Classno):
            __features__ = Features.EQ | Features.HASH
            __eq_keys__ = ('id',)
            __hash_keys__ = ('id',)
            id: int
            name: str

        class Extended(Base):
            __eq_keys__ = ('id', 'version')  # Override parent keys
            __hash_keys__ = ('id',)  # Keep parent hash keys
            version: int

        obj1 = Extended(id=1, name="test", version=1)
        obj2 = Extended(id=1, name="different", version=1)
        obj3 = Extended(id=1, name="test", version=2)

        # Equality based on id AND version
        assert obj1 == obj2  # Same id and version
        assert obj1 != obj3  # Different version

        # Hash still based on id only
        assert hash(obj1) == hash(obj2) == hash(obj3)

    def test_field_inheritance(self):
        """Test field inheritance including defaults."""
        class Base(Classno):
            __features__ = Features.EQ
            name: str
            items: List[str] = field(default_factory=list)
            config: Dict[str, str] = field(default_factory=dict)

        class Extended(Base):
            priority: int = 0
            extra_items: List[int] = field(default_factory=list)

        obj = Extended(name="test")

        # Should have all fields with proper defaults
        assert obj.name == "test"
        assert obj.items == []
        assert obj.config == {}
        assert obj.priority == 0
        assert obj.extra_items == []

        # Should have independent default objects
        obj2 = Extended(name="test2")
        obj.items.append("test")
        assert obj2.items == []  # Independent

    def test_multiple_inheritance(self):
        """Test multiple inheritance scenarios."""
        class Mixin1(Classno):
            __features__ = Features.EQ
            mixin1_field: str = "mixin1"

        class Mixin2(Classno):
            __features__ = Features.REPR
            mixin2_field: str = "mixin2"

        class Combined(Mixin1, Mixin2):
            __features__ = Features.EQ | Features.REPR | Features.ORDER
            main_field: str

        obj = Combined(main_field="main")

        # Should have fields from all parents
        assert obj.mixin1_field == "mixin1"
        assert obj.mixin2_field == "mixin2"
        assert obj.main_field == "main"

        # Should have combined features
        obj2 = Combined(main_field="main")
        assert obj == obj2  # EQ
        assert repr(obj)    # REPR
        assert obj <= obj2  # ORDER

    def test_deep_inheritance_chain(self):
        """Test deep inheritance chains."""
        class Level0(Classno):
            __features__ = Features.EQ
            level0_field: str = "level0"

        class Level1(Level0):
            level1_field: str = "level1"

        class Level2(Level1):
            __features__ = Features.EQ | Features.ORDER
            level2_field: str = "level2"

        class Level3(Level2):
            level3_field: str = "level3"

        obj = Level3()

        # Should have fields from all levels
        assert obj.level0_field == "level0"
        assert obj.level1_field == "level1"
        assert obj.level2_field == "level2"
        assert obj.level3_field == "level3"

        # Should have features from inheritance chain
        obj2 = Level3()
        assert obj == obj2  # EQ
        assert obj <= obj2  # ORDER

    def test_inheritance_with_validation(self):
        """Test inheritance with validation features."""
        class ValidatedBase(Classno):
            __features__ = Features.VALIDATION | Features.EQ
            name: str
            count: int

        class ValidatedExtended(ValidatedBase):
            items: List[str]
            optional_value: Optional[int] = None

        # Should validate all fields including inherited ones
        obj = ValidatedExtended(name="test", count=42, items=["a", "b"])
        assert obj.name == "test"
        assert obj.count == 42
        assert obj.items == ["a", "b"]
        assert obj.optional_value is None

        # Validation should work for base fields
        with pytest.raises(TypeError):
            ValidatedExtended(name=123, count=42, items=["a"])  # Invalid name type

        # Validation should work for extended fields
        with pytest.raises(TypeError):
            ValidatedExtended(name="test", count=42, items="not_a_list")

    def test_inheritance_with_casting(self):
        """Test inheritance with casting features."""
        class CastingBase(Classno):
            __features__ = Features.LOSSY_AUTOCAST | Features.EQ
            name: str
            numbers: List[int] = field(default_factory=list)

        class CastingExtended(CastingBase):
            mapping: Dict[str, int] = field(default_factory=dict)
            flexible: Union[str, int] = "default"

        # Should cast all fields including inherited ones
        obj = CastingExtended(
            name=123,  # Cast to string
            numbers=["1", "2", "3"],  # Cast to List[int]
            mapping={"a": "10", "b": "20"},  # Cast values to int
            flexible=42  # Union allows int
        )

        assert obj.name == "123"
        assert obj.numbers == [1, 2, 3]
        assert obj.mapping == {"a": 10, "b": 20}
        assert obj.flexible == 42

    def test_inheritance_with_frozen(self):
        """Test inheritance with frozen feature."""
        class FrozenBase(Classno):
            __features__ = Features.FROZEN | Features.EQ
            name: str

        class FrozenExtended(FrozenBase):
            value: int

        obj = FrozenExtended(name="test", value=42)

        # Should be frozen for all fields
        with pytest.raises(AttributeError):
            obj.name = "changed"  # Base field

        with pytest.raises(AttributeError):
            obj.value = 100  # Extended field

    def test_inheritance_with_private_fields(self):
        """Test inheritance with private field handling."""
        class PrivateBase(Classno):
            __features__ = Features.PRIVATE | Features.REPR | Features.EQ
            public_field: str
            _protected_field: str
            __private_field: str

        class PrivateExtended(PrivateBase):
            extended_public: str
            _extended_protected: str

        obj = PrivateExtended(
            public_field="public",
            _protected_field="protected",
            __private_field="private",
            extended_public="ext_public",
            _extended_protected="ext_protected"
        )

        # Repr should handle private fields properly
        repr_str = repr(obj)
        assert "public_field='public'" in repr_str
        assert "extended_public='ext_public'" in repr_str
        assert "_protected" not in repr_str  # Private fields hidden
        assert "__private" not in repr_str

    def test_abstract_like_inheritance(self):
        """Test abstract-like base class patterns."""
        class AbstractBase(Classno):
            __features__ = Features.EQ | Features.ORDER
            __order_keys__ = ('name',)

            name: str

            def get_info(self) -> str:
                """Abstract-like method."""
                raise NotImplementedError("Subclasses must implement")

        class ConcreteImpl(AbstractBase):
            value: int

            def get_info(self) -> str:
                return f"{self.name}: {self.value}"

        obj = ConcreteImpl(name="test", value=42)
        assert obj.get_info() == "test: 42"

        # Should have inherited features
        obj2 = ConcreteImpl(name="test", value=100)
        assert obj == obj2  # EQ (based on all fields)
        assert obj < ConcreteImpl(name="ztest", value=1)  # ORDER (based on name)

    def test_inheritance_with_slots(self):
        """Test inheritance with slots feature."""
        class SlotsBase(Classno):
            __features__ = Features.SLOTS | Features.EQ
            base_field: str

        class SlotsExtended(SlotsBase):
            extended_field: int

        obj = SlotsExtended(base_field="test", extended_field=42)

        # Should use slots
        assert not hasattr(obj, '__dict__')

        # Should have all fields accessible
        assert obj.base_field == "test"
        assert obj.extended_field == 42

    def test_mixin_patterns(self):
        """Test mixin patterns with classno."""
        class TimestampMixin(Classno):
            __features__ = Features.EQ
            created_at: Optional[str] = None
            updated_at: Optional[str] = None

        class ValidationMixin(Classno):
            __features__ = Features.VALIDATION
            # No fields, just adds validation feature

        class DataClass(TimestampMixin, ValidationMixin):
            __features__ = Features.EQ | Features.VALIDATION
            name: str
            data: List[str] = field(default_factory=list)

        obj = DataClass(
            name="test",
            data=["item1", "item2"],
            created_at="2023-01-01",
            updated_at="2023-01-02"
        )

        # Should have all mixin functionality
        assert obj.name == "test"
        assert obj.data == ["item1", "item2"]
        assert obj.created_at == "2023-01-01"
        assert obj.updated_at == "2023-01-02"

    def test_complex_inheritance_hierarchy(self):
        """Test complex inheritance hierarchy with all features."""
        class Entity(Classno):
            __features__ = Features.EQ | Features.HASH
            __eq_keys__ = ('id',)
            __hash_keys__ = ('id',)
            id: int
            name: str

        class TimestampedEntity(Entity):
            created_at: str
            updated_at: Optional[str] = None

        class ValidatedEntity(TimestampedEntity):
            __features__ = Features.EQ | Features.HASH | Features.VALIDATION
            # Inherits custom keys from Entity

        class User(ValidatedEntity):
            __features__ = Features.EQ | Features.HASH | Features.VALIDATION | Features.ORDER
            __order_keys__ = ('name', 'created_at')
            email: str
            roles: List[str] = field(default_factory=list)

        user1 = User(
            id=1,
            name="Alice",
            created_at="2023-01-01",
            email="alice@example.com",
            roles=["user", "admin"]
        )

        user2 = User(
            id=1,  # Same id
            name="Alice Updated",  # Different name
            created_at="2023-01-02",
            email="alice.updated@example.com",
            roles=["admin"]
        )

        # Equality based on id only (inherited from Entity)
        assert user1 == user2

        # Hash based on id only
        assert hash(user1) == hash(user2)

        # Ordering based on name, created_at (from User)
        user3 = User(id=2, name="Bob", created_at="2023-01-01", email="bob@example.com")
        assert user1 < user3  # "Alice" < "Bob"
