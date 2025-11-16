"""
Centralized error handling and message formatting for Classno library.

This module provides consistent error messages across all Classno modules,
making errors more predictable and easier to understand for users.
"""

import typing as t


class ErrorFormatter:
    """Centralized error message formatting."""

    @staticmethod
    def validation_error(
        field_name: str, expected_type: t.Any, actual_value: t.Any
    ) -> str:
        """Format a validation error message."""
        return (
            f"Validation error for field '{field_name}': "
            f"expected {expected_type}, got {actual_value!r} "
            f"of type {type(actual_value).__name__}"
        )

    @staticmethod
    def validation_no_handler(origin: t.Any) -> str:
        """Format error for missing validation handler."""
        return f"No validation handler available for type {origin}"

    @staticmethod
    def casting_error(value: t.Any, target_type: t.Any, reason: str = "") -> str:
        """Format a casting error message."""
        msg = f"Cannot cast {value!r} of type {type(value).__name__} to {target_type}"
        if reason:
            msg += f": {reason}"
        return msg

    @staticmethod
    def casting_no_handler(origin: t.Any) -> str:
        """Format error for missing casting handler."""
        return f"No casting handler available for type {origin}"

    @staticmethod
    def frozen_modify_error(class_name: str) -> str:
        """Format error for attempting to modify frozen object."""
        return f"Cannot modify attributes of frozen class {class_name}"

    @staticmethod
    def frozen_delete_error(class_name: str) -> str:
        """Format error for attempting to delete from frozen object."""
        return f"Cannot delete attributes from frozen class {class_name}"

    @staticmethod
    def private_write_error() -> str:
        """Format error for writing to private field without underscore."""
        return (
            "Cannot write to private fields directly. "
            "Use _fieldname to set private fields."
        )

    @staticmethod
    def private_not_found_error(field_name: str) -> str:
        """Format error for accessing non-existent private field."""
        return f"Private field '{field_name}' not found"

    @staticmethod
    def missing_required_fields(class_name: str, field_names: list[str]) -> str:
        """Format error for missing required fields."""
        fields_str = ", ".join(f"'{f}'" for f in field_names)
        return (
            f"{class_name}.__init__() missing {len(field_names)} "
            f"required argument{'s' if len(field_names) > 1 else ''}: {fields_str}"
        )

    @staticmethod
    def mutable_default_error(field_default: t.Any) -> str:
        """Format error for mutable default values."""
        type_name = type(field_default).__name__
        return (
            f"Mutable default values are not allowed. "
            f"Found {type_name} {field_default!r}. "
            f"Use default_factory=lambda: {field_default!r} instead "
            f"to avoid shared state issues."
        )
