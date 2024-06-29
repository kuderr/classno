from netsome import types as nst
import random
import classno


def random_asn():
    number = random.randint(65000, 65535)
    return nst.ASN(number)


class SubClassno(classno.Classno):

    __features__ = classno.Features.DEFAULT | classno.Features.PRIVATE

    a: int = 1
    b: str = classno.field(default="foobar")
    c: nst.IPv4Address = classno.field(default_factory=random_asn)
    d: list[str] = ["Foo", "Bar"]


t = SubClassno()