import types

from classno import constants as c


def field(*, default=c.MISSING, default_factory=c.MISSING, metadata=None):
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
        type_name = type(default_value).__name__
        example_factory = f"lambda: {default_value!r}"

        raise ValueError(
            f"Mutable default values are not allowed. "
            f"Found {type_name} {default_value!r}. "
            f"Use default_factory={example_factory} instead to avoid shared state issues."
        )
