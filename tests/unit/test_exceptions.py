"""Tests for exception classes and error handling."""

import pytest

from classno import Classno
from classno import Features
from classno.exceptions import BaseErrorsCollection
from classno.exceptions import CastingError
from classno.exceptions import ValidationError


class TestExceptionHierarchy:
    """Test exception class hierarchy and initialization."""

    def test_base_errors_collection_initialization(self):
        """Test BaseErrorsCollection stores errors and formats message."""
        errors = ["Error 1", "Error 2", "Error 3"]
        exc = BaseErrorsCollection(errors)

        assert hasattr(exc, "errors")
        assert exc.errors == errors

        msg = str(exc)
        assert "Error 1" in msg
        assert "Error 2" in msg
        assert "Error 3" in msg

    def test_validation_error_inherits_from_type_error(self):
        """Test ValidationError inherits from TypeError."""
        errors = ["Validation failed"]
        exc = ValidationError(errors)

        assert isinstance(exc, TypeError)
        assert isinstance(exc, BaseErrorsCollection)
        assert "Validation failed" in str(exc)

    def test_casting_error_inherits_from_type_error(self):
        """Test CastingError inherits from TypeError."""
        errors = ["Casting failed"]
        exc = CastingError(errors)

        assert isinstance(exc, TypeError)
        assert isinstance(exc, BaseErrorsCollection)
        assert "Casting failed" in str(exc)


class TestExceptionRaising:
    """Test that exceptions are properly raised in actual usage."""

    def test_validation_error_raised_with_invalid_types(self):
        """Test ValidationError is raised when validation fails."""

        class ValidatedClass(Classno):
            __features__ = Features.VALIDATION
            age: int
            name: str

        with pytest.raises(ValidationError) as exc_info:
            ValidatedClass(age="not_int", name=123)

        error_msg = str(exc_info.value)
        assert "age" in error_msg or "name" in error_msg

    def test_casting_error_raised_when_cast_impossible(self):
        """Test CastingError is raised when casting fails."""

        class CastClass(Classno):
            __features__ = Features.LOSSY_AUTOCAST | Features.VALIDATION
            numbers: list[int]

        with pytest.raises(CastingError) as exc_info:
            CastClass(numbers=object())

        assert isinstance(exc_info.value, CastingError)
