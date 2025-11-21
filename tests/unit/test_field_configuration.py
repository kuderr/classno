"""Tests for field() configuration function."""

import pytest

from classno import field
from classno._fields import Field
from classno.constants import MISSING


class TestFieldFunction:
    """Test field() factory function."""

    def test_field_with_default(self):
        """Test field() with default value."""
        f = field(default="test")

        assert isinstance(f, Field)
        assert f.default == "test"
        assert f.default_factory is MISSING

    def test_field_with_default_factory(self):
        """Test field() with default_factory."""
        f = field(default_factory=list)

        assert isinstance(f, Field)
        assert f.default is MISSING
        assert f.default_factory is list

    def test_field_with_metadata(self):
        """Test field() with metadata."""
        f = field(default="test", metadata={"indexed": True, "key": "value"})

        assert f.metadata["indexed"] is True
        assert f.metadata["key"] == "value"
        # Metadata should be immutable (MappingProxyType)
        from types import MappingProxyType

        assert isinstance(f.metadata, MappingProxyType)

    def test_field_cannot_have_both_default_and_factory(self):
        """Test that field() raises error if both default and factory specified."""
        with pytest.raises(ValueError) as exc_info:
            field(default="test", default_factory=list)

        assert "cannot specify both" in str(exc_info.value)

    def test_field_repr(self):
        """Test Field __repr__ shows all attributes."""
        f = Field(default="test", default_factory=MISSING, metadata={"key": "val"})
        f.name = "test_field"
        f.hint = str

        repr_str = repr(f)
        assert "Field(" in repr_str
        assert "name='test_field'" in repr_str
        assert "hint=" in repr_str


class TestFieldValidation:
    """Test field validation for mutable defaults."""

    def test_field_rejects_list_default(self):
        """Test field() rejects list as default."""
        with pytest.raises(ValueError) as exc_info:
            field(default=[])

        error_msg = str(exc_info.value)
        assert "Mutable default" in error_msg
        assert "default_factory" in error_msg

    def test_field_rejects_dict_default(self):
        """Test field() rejects dict as default."""
        with pytest.raises(ValueError):
            field(default={})

    def test_field_rejects_set_default(self):
        """Test field() rejects set as default."""
        with pytest.raises(ValueError):
            field(default=set())

    def test_field_accepts_immutable_defaults(self):
        """Test field() accepts immutable defaults."""
        # These should all work
        field(default="string")
        field(default=42)
        field(default=3.14)
        field(default=True)
        field(default=None)
        field(default=(1, 2, 3))  # Tuple is immutable
