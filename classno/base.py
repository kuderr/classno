"""
Features:
- set fields from class attrs
- set __init__, __repr__, __hash__, __eq__, etc.
- save annotations and basic types (dict[str, int] -> dict)

More stuff:
- implement features from popular analogs: frozen, `a: str = field(...)`, etc.
- a: str = field(private=True), allows get, disables set on self.a. Creates self._a that is rw
- Autovalidating, if needed
- Autocasting: strict/lossless or lossy, if needed
- go deep through annotation and validate/cast stuff

NOTES:
- use typing.t.get_type_hints, its better then inspect.get_annotations
"""

# netsome here ofc
from netsome import types as nst
from dataclasses import dataclass, Field as f
import typing as t

import types


class Foo:
    a: str
    b: int
    ip: nst.IPv4Address

    d: dict[str, int]
    d2: dict[str, list[bool]]


class Foo1(Foo): ...


class Foo2(Foo):
    a: int = 2


####
class MissingType: ...


MISSING = MissingType
_FIELDS = "_FIELDS"


class Field:
    def __init__(self, default, default_factory, metadata):
        self.name = None
        self.hint = None
        self.default = default
        self.default_factory = default_factory
        self.metadata = types.MappingProxyType(metadata or {})

    def __repr__(self) -> str:
        return (
            "Field("
            f"name={self.name!r}, "
            f"hint={self.hint!r}, "
            f"default={self.default!r}, "
            f"default_factory={self.default_factory!r}, "
            f"metadata={self.metadata!r}"
            ")"
        )


def field(*, default=MISSING, default_factory=MISSING, metadata=None):
    if default is not MISSING and default_factory is not MISSING:
        raise ValueError("cannot specify both default and default_factory")

    return Field(default, default_factory, metadata)


def _get_tuple(obj):
    return tuple(getattr(obj, f.name) for f in obj._FIELDS.values())


class Classno:
    def __init_subclass__(cls):
        hints = t.get_type_hints(cls)

        fields = {}
        for name, hint in hints.items():
            default = getattr(cls, name, MISSING)
            if isinstance(default, Field):
                f = default
            else:
                if isinstance(default, types.MemberDescriptorType):
                    default = MISSING
                f = field(default=default)

            f.name = name
            f.hint = hint

            fields[name] = f

        setattr(cls, _FIELDS, fields)

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

        missing_required_pos_args = []
        for field in self._FIELDS.values():
            if hasattr(self, field.name) and not isinstance(
                getattr(self, field.name), Field
            ):
                continue

            if field.default is not MISSING:
                setattr(self, field.name, field.default)
            elif field.default_factory is not MISSING:
                setattr(self, field.name, field.default_factory())
            else:
                missing_required_pos_args.append(field.name)

        if missing_required_pos_args:
            raise TypeError(
                f"{self.__class__.__name__}.__init__() missing {len(missing_required_pos_args)} required positional arguments: {', '.join(f'{arg}' for arg in missing_required_pos_args)}"
            )

    def __repr__(self) -> str:
        fields = ", ".join(
            f"{f.name}={getattr(self, f.name)!r}" for f in self._FIELDS.values()
        )
        return f"{self.__class__.__name__}({fields})"

    def __hash__(self) -> int:
        return hash(_get_tuple(self))

    def __eq__(self, other: object) -> bool:
        if not (other.__class__ is self.__class__):
            return NotImplemented

        return _get_tuple(self) == _get_tuple(other)


class Test(Classno):
    a: int = 1
    b: str = field(default="foobar")
    c: "str"
    d: nst.IPv4Address = field(default_factory=lambda: nst.IPv4Address("1.1.1.1"))
    e: list[nst.ASN]


t = Test()
