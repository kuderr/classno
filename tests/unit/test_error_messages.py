"""Tests for error message formatting."""

from classno._errors import ErrorFormatter


class TestErrorFormatterMessages:
    """Test ErrorFormatter produces correct error messages."""

    def test_validation_error_message(self):
        """Test validation error message format."""
        msg = ErrorFormatter.validation_error("age", int, "not_an_int")

        assert "Validation error" in msg
        assert "age" in msg
        assert "int" in msg
        assert "not_an_int" in msg

    def test_validation_no_handler_message(self):
        """Test validation no handler error message."""
        msg = ErrorFormatter.validation_no_handler(list)

        assert "No validation handler" in msg
        assert "list" in msg

    def test_casting_error_message(self):
        """Test casting error message format."""
        msg = ErrorFormatter.casting_error("value", int, "cannot convert")

        assert "Cannot cast" in msg
        assert "value" in msg
        assert "int" in msg
        assert "cannot convert" in msg

    def test_casting_no_handler_message(self):
        """Test casting no handler error message."""
        msg = ErrorFormatter.casting_no_handler(dict)

        assert "No casting handler" in msg
        assert "dict" in msg

    def test_frozen_modify_error_message(self):
        """Test frozen modify error message."""
        msg = ErrorFormatter.frozen_modify_error("MyClass")

        assert "Cannot modify" in msg
        assert "frozen" in msg.lower()
        assert "MyClass" in msg

    def test_frozen_delete_error_message(self):
        """Test frozen delete error message."""
        msg = ErrorFormatter.frozen_delete_error("MyClass")

        assert "Cannot delete" in msg
        assert "frozen" in msg.lower()
        assert "MyClass" in msg

    def test_private_write_error_message(self):
        """Test private write error message."""
        msg = ErrorFormatter.private_write_error()

        assert "Cannot write to private fields" in msg
        assert "_fieldname" in msg.lower()

    def test_private_not_found_error_message(self):
        """Test private not found error message."""
        msg = ErrorFormatter.private_not_found_error("_missing")

        assert "not found" in msg
        assert "_missing" in msg

    def test_missing_required_fields_message(self):
        """Test missing required fields error message."""
        msg = ErrorFormatter.missing_required_fields("User", ["name", "age"])

        assert "User" in msg
        assert "name" in msg
        assert "age" in msg
        assert "2" in msg or "required" in msg.lower()

    def test_mutable_default_error_message(self):
        """Test mutable default error message."""
        msg = ErrorFormatter.mutable_default_error([1, 2, 3])

        assert "Mutable default" in msg
        assert "default_factory" in msg
        assert "[1, 2, 3]" in msg or "list" in msg.lower()
