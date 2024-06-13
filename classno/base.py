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

from netsome import types as nst
from dataclasses import dataclass, Field as f

from classno import root


class Foo:
    a: str
    b: int
    ip: nst.IPv4Address

    d: dict[str, int]
    d2: dict[str, list[bool]]


class Foo1(Foo): ...


class Foo2(Foo):
    a: int = 2


class Test(root.Classno):
    a: int = 1
    b: str = root.field(default="foobar")
    c: "str"
    d: nst.IPv4Address = root.field(default_factory=lambda: nst.IPv4Address("1.1.1.1"))
    e: list[nst.ASN]


t = Test()
