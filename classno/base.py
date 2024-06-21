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

from classno import root


class Test(root.Classno):
    __features__ = root.Features.DEFAULT | root.Features.PRIVATE

    a: int = 1
    b: str = root.field(default="foobar")
    c: "str" = root.field()
    d: nst.IPv4Address = root.field(default_factory=lambda: nst.IPv4Address("1.1.1.1"))
    e: list[nst.ASN] = 1


t = Test()
