"""
Features:
- save annotations and basic types (dict[str, int] -> dict) ?

More stuff:
- Autovalidating, if needed
- Autocasting: strict/lossless or lossy, if needed
- go deep through annotation and validate/cast stuff

Later:
- features on fields
- can set cached properties if immutable ?

"""

from netsome import types as nst

import classno


class Test(classno.Classno):
    __features__ = (
        classno.Features.DEFAULT | classno.Features.HASH | classno.Features.PRIVATE
    )

    a: int = 1
    b: str = classno.field(default="foobar")
    c: "str" = classno.field(default="gg")
    d: nst.IPv4Address = classno.field(
        default_factory=lambda: nst.IPv4Address("1.1.1.1")
    )
    e: list[nst.ASN] = 1


t = Test()
