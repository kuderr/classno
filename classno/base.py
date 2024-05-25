# netsome here ofc
from ipaddress import IPv4Address

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
"""


class Foo:
    a: str
    b: int
    ip: IPv4Address

    d: dict[str, int]
    d2: dict[str, list[bool]]
