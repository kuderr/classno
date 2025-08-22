import pytest
from typing import Optional

import classno
from classno import Classno, Features, field
from classno import exceptions as excs


class TestInheritance:
    """Test inheritance scenarios and behavior."""

    def test_basic_inheritance(self):
        """Test basic inheritance of Classno classes."""

        class Animal(Classno):
            name: str
            species: str

        class Dog(Animal):
            breed: str
            age: int = 0

        dog = Dog(name="Buddy", species="Canine", breed="Golden Retriever", age=5)

        assert dog.name == "Buddy"
        assert dog.species == "Canine"
        assert dog.breed == "Golden Retriever"
        assert dog.age == 5

    def test_feature_inheritance(self):
        """Test inheritance of features from parent classes."""

        class BaseWithFeatures(Classno):
            __features__ = Features.EQ | Features.HASH
            id: int
            name: str

        class ChildClass(BaseWithFeatures):
            description: str

        obj1 = ChildClass(id=1, name="test", description="desc")
        obj2 = ChildClass(id=1, name="test", description="desc")
        obj3 = ChildClass(id=2, name="test", description="desc")

        # Should inherit equality from parent
        assert obj1 == obj2
        assert obj1 != obj3

        # Should inherit hash from parent
        obj_set = {obj1, obj2, obj3}
        assert len(obj_set) == 2

    def test_feature_override(self):
        """Test overriding features in child classes."""

        class BaseClass(Classno):
            __features__ = Features.EQ
            name: str
            value: int

        class FrozenChild(BaseClass):
            __features__ = Features.EQ | Features.FROZEN
            extra: str = "default"

        class ValidatedChild(BaseClass):
            __features__ = Features.EQ | Features.VALIDATION
            score: float = 0.0

        # Base should be mutable
        base = BaseClass(name="base", value=1)
        base.name = "modified"
        assert base.name == "modified"

        # Frozen child should be immutable
        frozen = FrozenChild(name="frozen", value=2, extra="test")
        with pytest.raises(Exception):
            frozen.name = "changed"

        # Validated child should validate types
        validated = ValidatedChild(name="valid", value=3, score=95.5)
        assert validated.score == 95.5

        with pytest.raises(excs.ValidationError):
            ValidatedChild(name="invalid", value="not an int")

    def test_custom_keys_inheritance(self):
        """Test inheritance of custom comparison keys."""

        class BaseWithKeys(Classno):
            __eq_keys__ = {"id"}
            __hash_keys__ = {"id"}
            __features__ = Features.EQ | Features.HASH

            id: int
            name: str

        class ChildWithAdditionalKeys(BaseWithKeys):
            __eq_keys__ = {"id", "version"}  # Override parent keys
            __hash_keys__ = {"id"}  # Keep parent hash keys

            version: str
            data: str = "default"

        parent1 = BaseWithKeys(id=1, name="name1")
        parent2 = BaseWithKeys(id=1, name="name2")

        # Parents should be equal based on ID only
        assert parent1 == parent2

        child1 = ChildWithAdditionalKeys(
            id=1, version="1.0", name="child1", data="data1"
        )
        child2 = ChildWithAdditionalKeys(
            id=1, version="1.0", name="child2", data="data2"
        )
        child3 = ChildWithAdditionalKeys(
            id=1, version="2.0", name="child1", data="data1"
        )

        # Children should be equal based on ID and version
        assert child1 == child2  # Same id and version
        assert child1 != child3  # Same id, different version

        # Hash should still be based on ID only
        assert hash(child1) == hash(child2) == hash(child3)

    def test_deep_inheritance_chain(self):
        """Test deep inheritance chains."""

        class Animal(Classno):
            __features__ = Features.EQ
            name: str
            species: str

        class Mammal(Animal):
            fur_color: str = "brown"
            warm_blooded: bool = True

        class Carnivore(Mammal):
            diet: str = "meat"
            hunting_style: str = "pack"

        class Canine(Carnivore):
            pack_size: int = 5
            territory_size: float = 10.0

        class Wolf(Canine):
            alpha: bool = False
            howl_frequency: float = 1.5

        wolf = Wolf(
            name="Grey Wolf",
            species="Canis lupus",
            fur_color="grey",
            hunting_style="pack",
            pack_size=8,
            alpha=True,
            howl_frequency=2.0,
        )

        # Should have all inherited fields
        assert wolf.name == "Grey Wolf"
        assert wolf.species == "Canis lupus"
        assert wolf.warm_blooded is True  # From Mammal
        assert wolf.diet == "meat"  # From Carnivore
        assert wolf.pack_size == 8  # Overridden default
        assert wolf.alpha is True  # From Wolf

        # Should inherit equality feature
        wolf2 = Wolf(
            name="Grey Wolf",
            species="Canis lupus",
            fur_color="grey",
            hunting_style="pack",
            pack_size=8,
            alpha=True,
            howl_frequency=2.0,
        )
        assert wolf == wolf2

    def test_multiple_inheritance_mixin_pattern(self):
        """Test multiple inheritance with mixin-like patterns."""

        class TimestampMixin(Classno):
            created_at: float = 0.0
            updated_at: float = 0.0

        class VersionMixin(Classno):
            version: str = "1.0"
            revision: int = 1

        class Document(TimestampMixin, VersionMixin):
            title: str
            content: str = ""

        doc = Document(
            title="Test Document",
            content="Some content",
            created_at=1234567890.0,
            version="2.0",
            revision=5,
        )

        assert doc.title == "Test Document"
        assert doc.created_at == 1234567890.0  # From TimestampMixin
        assert doc.version == "2.0"  # From VersionMixin
        assert doc.updated_at == 0.0  # Default from TimestampMixin

    def test_abstract_base_pattern(self):
        """Test abstract base class pattern."""

        class Shape(Classno):
            __features__ = Features.EQ | Features.HASH
            name: str
            color: str = "white"

            # Abstract-like method (not enforced, but shows pattern)
            def area(self) -> float:
                raise NotImplementedError("Subclasses must implement area()")

        class Rectangle(Shape):
            width: float
            height: float

            def area(self) -> float:
                return self.width * self.height

        class Circle(Shape):
            radius: float

            def area(self) -> float:
                return 3.14159 * self.radius**2

        rect = Rectangle(name="rectangle", width=10.0, height=5.0, color="red")
        circle = Circle(name="circle", radius=3.0, color="blue")

        assert rect.area() == 50.0
        assert abs(circle.area() - 28.274) < 0.01  # Approximate π * 3²

        # Should have inherited features
        rect2 = Rectangle(name="rectangle", width=10.0, height=5.0, color="red")
        assert rect == rect2
        assert hash(rect) == hash(rect2)

    def test_inheritance_with_validation(self):
        """Test inheritance combined with validation features."""

        class ValidatedBase(Classno):
            __features__ = Features.VALIDATION
            id: int
            name: str

        class ValidatedChild(ValidatedBase):
            scores: list[float]
            metadata: dict[str, str] = field(default_factory=dict)

        # Should validate all fields including inherited ones
        child = ValidatedChild(id=1, name="test", scores=[95.5, 87.2, 92.0])
        assert child.id == 1
        assert child.scores == [95.5, 87.2, 92.0]

        # Should validate inherited fields
        with pytest.raises(excs.ValidationError):
            ValidatedChild(id="not an int", name="test", scores=[])

        # Should validate new fields
        with pytest.raises(excs.ValidationError):
            ValidatedChild(id=1, name="test", scores="not a list")

    def test_inheritance_with_frozen(self):
        """Test inheritance with frozen features."""

        class MutableBase(Classno):
            base_field: str

        class FrozenChild(MutableBase):
            __features__ = Features.FROZEN
            child_field: int

        # Base should be mutable
        base = MutableBase(base_field="test")
        base.base_field = "modified"
        assert base.base_field == "modified"

        # Child should be completely frozen (including inherited fields)
        child = FrozenChild(base_field="test", child_field=42)

        with pytest.raises(Exception):
            child.base_field = "changed"  # Inherited field should be frozen

        with pytest.raises(Exception):
            child.child_field = 99  # Own field should be frozen

    def test_field_override_in_inheritance(self):
        """Test overriding field definitions in child classes."""

        class BaseWithDefaults(Classno):
            name: str = "default_name"
            value: int = 0
            active: bool = True

        class ChildWithNewDefaults(BaseWithDefaults):
            name: str = "child_default"  # Override default
            value: int = 100  # Override default
            extra: str = "extra"

        # Base uses original defaults
        base = BaseWithDefaults()
        assert base.name == "default_name"
        assert base.value == 0
        assert base.active is True

        # Child uses overridden defaults
        child = ChildWithNewDefaults()
        assert child.name == "child_default"
        assert child.value == 100
        assert child.active is True  # Inherited default
        assert child.extra == "extra"

    def test_complex_inheritance_with_nested_objects(self):
        """Test inheritance with complex nested object structures."""

        class Address(Classno):
            street: str
            city: str
            country: str = "USA"

        class PersonBase(Classno):
            name: str
            age: int
            address: Optional[Address] = None

        class Employee(PersonBase):
            __features__ = Features.VALIDATION | Features.EQ
            employee_id: int
            department: str
            manager: Optional["Employee"] = None

        address = Address(street="123 Main St", city="Boston")
        manager = Employee(
            name="Manager",
            age=45,
            employee_id=1001,
            department="Engineering",
            address=address,
        )

        employee = Employee(
            name="John",
            age=30,
            employee_id=1002,
            department="Engineering",
            manager=manager,
            address=address,
        )

        # Should handle nested inheritance properly
        assert employee.name == "John"  # From PersonBase
        assert employee.employee_id == 1002  # From Employee
        assert employee.address.street == "123 Main St"  # Nested object
        assert employee.manager.name == "Manager"  # Self-referential
        assert employee.manager.employee_id == 1001

        # Should validate inherited fields
        with pytest.raises(TypeError):
            Employee(name=123, age=30, employee_id=1003, department="IT")

    def test_inheritance_method_resolution_order(self):
        """Test that method resolution order works correctly with Classno."""

        class A(Classno):
            a_field: str = "A"

        class B(A):
            b_field: str = "B"

        class C(A):
            c_field: str = "C"

        class D(B, C):  # Multiple inheritance
            d_field: str = "D"

        obj = D()
        assert obj.a_field == "A"  # From A
        assert obj.b_field == "B"  # From B
        assert obj.c_field == "C"  # From C
        assert obj.d_field == "D"  # From D

        # Should work with all inherited fields
        obj2 = D(a_field="modified_A", b_field="modified_B")
        assert obj2.a_field == "modified_A"
        assert obj2.b_field == "modified_B"
        assert obj2.c_field == "C"  # Default from C
