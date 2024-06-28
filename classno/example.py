from netsome import types as nst

import classno


class Test(classno.Classno):
    __features__ = (
        classno.Features.DEFAULT
        | classno.Features.HASH
        | classno.Features.PRIVATE
        | classno.Features.VALIDATION
    )

    a: int = 1
    b: str = classno.field(default="foobar")
    c: "str" = classno.field(default="gg")
    d: nst.IPv4Address = classno.field(
        default_factory=lambda: nst.IPv4Address("1.1.1.1")
    )
    e: list[nst.ASN] = [nst.ASN(65535)]


t = Test()
t2 = Test()
