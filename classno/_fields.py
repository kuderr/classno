import types

from classno import constants as c


def field(*, default=c.MISSING, default_factory=c.MISSING, metadata=None):
    if default is not c.MISSING and default_factory is not c.MISSING:
        raise ValueError("cannot specify both default and default_factory")

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
