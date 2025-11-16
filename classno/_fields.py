import types

from classno import _errors
from classno import constants as c


def field(*, default=c.MISSING, default_factory=c.MISSING, metadata=None):
    """
    Define a field with custom configuration.

    This function creates a Field object that can be used to specify default
    values, factory functions, and metadata for class fields.

    Args:
        default: Default value for the field (cannot be used with default_factory).
                 Mutable defaults (list, dict, set) are not allowed.
        default_factory: Callable that returns a default value
                        (cannot be used with default).
                        Use this for mutable defaults like lists or dicts.
        metadata: Optional dictionary of metadata for the field.

    Returns:
        Field: A Field object with the specified configuration.

    Raises:
        ValueError: If both default and default_factory are specified, or if
                   a mutable default value is provided without using default_factory.

    Example:
        ```python
        from classno import Classno, field

        class User(Classno):
            name: str
            tags: list = field(default_factory=list)
            metadata: dict = field(default_factory=dict, metadata={"indexed": True})
        ```
    """
    if default is not c.MISSING and default_factory is not c.MISSING:
        raise ValueError("cannot specify both default and default_factory")

    # Validate mutable defaults
    if default is not c.MISSING:
        _validate_field_default(default)

    return Field(default, default_factory, metadata)


class Field:
    def __init__(self, default, default_factory, metadata):
        self.name = None
        self.hint = None
        self.default = default
        self.default_factory = default_factory
        self.metadata = types.MappingProxyType(metadata or {})

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"name={self.name!r}, "
            f"hint={self.hint!r}, "
            f"default={self.default!r}, "
            f"default_factory={self.default_factory!r}, "
            f"metadata={self.metadata!r}"
            ")"
        )


def _validate_field_default(default_value):
    """Validate that mutable objects use default_factory instead of default."""
    # Check if default is a mutable type that could cause shared state issues
    mutable_types = (list, dict, set, bytearray)

    if isinstance(default_value, mutable_types):
        raise ValueError(_errors.ErrorFormatter.mutable_default_error(default_value))
