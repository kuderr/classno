from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

import pytest

from classno import Classno
from classno import Features
from classno import field
from classno.exceptions import ValidationError


class TestValidationFeature:
    """Test type validation functionality."""

    def test_basic_type_validation(self):
        """Test basic type validation for primitive types."""

        class ValidatedModel(Classno):
            __features__ = Features.VALIDATION
            name: str
            age: int
            score: float
            active: bool

        # Valid creation
        model = ValidatedModel(name="John", age=30, score=95.5, active=True)
        assert model.name == "John"
        assert model.age == 30
        assert model.score == 95.5
        assert model.active is True

        # Invalid types should raise ValidationError
        with pytest.raises(ValidationError):
            ValidatedModel(
                name=123, age=30, score=95.5, active=True
            )  # name should be str

        with pytest.raises(ValidationError):
            ValidatedModel(
                name="John", age="30", score=95.5, active=True
            )  # age should be int

        with pytest.raises(ValidationError):
            ValidatedModel(
                name="John", age=30, score="95.5", active=True
            )  # score should be float

        with pytest.raises(ValidationError):
            ValidatedModel(
                name="John", age=30, score=95.5, active="yes"
            )  # active should be bool

    def test_list_validation(self):
        """Test validation of list types."""

        class ListModel(Classno):
            __features__ = Features.VALIDATION
            numbers: List[int]
            names: List[str]
            mixed: List[Union[int, str]]

        # Valid lists
        model = ListModel(
            numbers=[1, 2, 3, 4, 5],
            names=["Alice", "Bob", "Charlie"],
            mixed=[1, "hello", 42, "world"],
        )
        assert model.numbers == [1, 2, 3, 4, 5]
        assert model.names == ["Alice", "Bob", "Charlie"]
        assert model.mixed == [1, "hello", 42, "world"]

        # Invalid list types
        with pytest.raises(ValidationError):
            ListModel(numbers="not a list", names=[], mixed=[])

        with pytest.raises(ValidationError):
            ListModel(numbers=[1, "2", 3], names=[], mixed=[])  # "2" is not int

        with pytest.raises(ValidationError):
            ListModel(numbers=[], names=[1, 2, 3], mixed=[])  # numbers in names

    def test_dict_validation(self):
        """Test validation of dictionary types."""

        class DictModel(Classno):
            __features__ = Features.VALIDATION
            str_to_int: Dict[str, int]
            int_to_list: Dict[int, List[str]]
            flexible: Dict[str, Union[int, str]]

        # Valid dictionaries
        model = DictModel(
            str_to_int={"a": 1, "b": 2, "c": 3},
            int_to_list={1: ["hello"], 2: ["world", "test"]},
            flexible={"num": 42, "text": "hello", "other": 100},
        )
        assert model.str_to_int == {"a": 1, "b": 2, "c": 3}
        assert model.int_to_list == {1: ["hello"], 2: ["world", "test"]}
        assert model.flexible == {"num": 42, "text": "hello", "other": 100}

        # Invalid dictionary types
        with pytest.raises(ValidationError):
            DictModel(
                str_to_int={1: "wrong"}, int_to_list={}, flexible={}
            )  # key should be str

        with pytest.raises(ValidationError):
            DictModel(
                str_to_int={"a": "wrong"}, int_to_list={}, flexible={}
            )  # value should be int

    def test_tuple_validation(self):
        """Test validation of tuple types."""

        class TupleModel(Classno):
            __features__ = Features.VALIDATION
            coordinates: Tuple[float, float]
            fixed_size: Tuple[int, str, bool]
            variable: Tuple[int, ...]

        # Valid tuples
        model = TupleModel(
            coordinates=(10.5, 20.3),
            fixed_size=(42, "hello", True),
            variable=(1, 2, 3, 4, 5),
        )
        assert model.coordinates == (10.5, 20.3)
        assert model.fixed_size == (42, "hello", True)
        assert model.variable == (1, 2, 3, 4, 5)

        # Invalid tuple types
        with pytest.raises(ValidationError):
            TupleModel(
                coordinates=("a", "b"), fixed_size=(1, "test", True), variable=(1, 2)
            )

        with pytest.raises(ValidationError):
            TupleModel(
                coordinates=(1.0, 2.0), fixed_size=(1, 2, 3), variable=(1, 2)
            )  # wrong type in fixed_size

    def test_optional_validation(self):
        """Test validation with Optional types."""

        class OptionalModel(Classno):
            __features__ = Features.VALIDATION
            name: str
            age: Optional[int] = None
            email: Optional[str] = None

        # Valid with None values
        model1 = OptionalModel(name="John")
        assert model1.name == "John"
        assert model1.age is None
        assert model1.email is None

        # Valid with actual values
        model2 = OptionalModel(name="Jane", age=25, email="jane@example.com")
        assert model2.name == "Jane"
        assert model2.age == 25
        assert model2.email == "jane@example.com"

        # Invalid types (not None and not the expected type)
        with pytest.raises(ValidationError):
            OptionalModel(name="John", age="invalid")

        with pytest.raises(ValidationError):
            OptionalModel(name="John", email=123)

    def test_union_validation(self):
        """Test validation with Union types."""

        class UnionModel(Classno):
            __features__ = Features.VALIDATION
            value: Union[int, str]
            number: Union[int, float]
            complex_union: Union[List[int], Dict[str, int]]

        # Valid union values
        model1 = UnionModel(value=42, number=10, complex_union=[1, 2, 3])
        assert model1.value == 42
        assert model1.number == 10
        assert model1.complex_union == [1, 2, 3]

        model2 = UnionModel(value="hello", number=3.14, complex_union={"a": 1, "b": 2})
        assert model2.value == "hello"
        assert model2.number == 3.14
        assert model2.complex_union == {"a": 1, "b": 2}

        # Invalid union values
        with pytest.raises(ValidationError):
            UnionModel(
                value=[], number=10, complex_union=[1, 2, 3]
            )  # list not in Union[int, str]

        with pytest.raises(ValidationError):
            UnionModel(
                value=42, number="invalid", complex_union=[1, 2, 3]
            )  # str not in Union[int, float]

    def test_nested_type_validation(self):
        """Test validation of complex nested types."""

        class NestedModel(Classno):
            __features__ = Features.VALIDATION
            matrix: List[List[int]]
            lookup: Dict[str, Dict[str, float]]
            complex_structure: Dict[str, List[Tuple[int, str]]]

        # Valid nested structures
        model = NestedModel(
            matrix=[[1, 2, 3], [4, 5, 6], [7, 8, 9]],
            lookup={"group1": {"a": 1.0, "b": 2.0}, "group2": {"c": 3.0}},
            complex_structure={
                "items": [(1, "first"), (2, "second")],
                "other": [(10, "ten"), (20, "twenty")],
            },
        )
        assert model.matrix == [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        assert model.lookup == {"group1": {"a": 1.0, "b": 2.0}, "group2": {"c": 3.0}}
        assert model.complex_structure["items"] == [(1, "first"), (2, "second")]

        # Invalid nested structures
        with pytest.raises(ValidationError):
            NestedModel(
                matrix=[[1, "invalid", 3]],  # string in list of ints
                lookup={},
                complex_structure={},
            )

        with pytest.raises(ValidationError):
            NestedModel(
                matrix=[[1, 2, 3]],
                lookup={"group": {"key": "invalid"}},  # string instead of float
                complex_structure={},
            )

    def test_validation_with_defaults(self):
        """Test that validation works with default values."""

        class DefaultValidatedModel(Classno):
            __features__ = Features.VALIDATION
            name: str
            numbers: List[int] = field(default_factory=list)
            mapping: Dict[str, int] = field(default_factory=dict)
            score: float = 0.0

        # Should work with defaults
        model = DefaultValidatedModel(name="test")
        assert model.name == "test"
        assert model.numbers == []
        assert model.mapping == {}
        assert model.score == 0.0

    def test_validation_error_messages(self):
        """Test that validation errors provide helpful messages."""

        class MessageModel(Classno):
            __features__ = Features.VALIDATION
            name: str
            age: int

        try:
            MessageModel(name=123, age=25)
            assert False, "Should have raised ValidationError"
        except ValidationError as e:
            # Error message should indicate the field and expected type
            assert "name" in str(e) or "str" in str(e)

    def test_validation_combined_with_other_features(self):
        """Test validation combined with other features."""

        class CombinedModel(Classno):
            __features__ = Features.VALIDATION | Features.EQ | Features.FROZEN
            name: str
            value: int

        # Should validate on creation
        model1 = CombinedModel(name="test", value=42)
        model2 = CombinedModel(name="test", value=42)

        # Should support equality
        assert model1 == model2

        # Should be frozen (immutable)
        with pytest.raises(Exception):
            model1.name = "changed"

        # Should still validate
        with pytest.raises(ValidationError):
            CombinedModel(name=123, value=42)
