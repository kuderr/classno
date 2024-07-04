from netsome import types as nst
import random
import classno


def random_ipv4():
    number = random.randint(65000, 65535)
    return nst.IPv4Address.from_int(number)


class SubClassno(classno.Classno):

    __features__ = classno.Features.DEFAULT | classno.Features.VALIDATION

    a: int = 1
    b: str = classno.field(default="foobar")
    c: nst.IPv4Address = classno.field(default_factory=random_ipv4)
    d: list[str] = ["Foo", "Bar"]


t = SubClassno()
