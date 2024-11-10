import random

from netsome import types as nst

import classno


def random_ipv4():
    number = random.randint(65000, 65535)
    return nst.IPv4Address.from_int(number)


class SubClassno(classno.Classno):
    __hash_keys__ = {"a"}
    __eq_keys__ = {"a", "b"}
    __order_keys__ = {"b", "c", "d"}

    a: int = 1
    b: str = classno.field(default="foobar")
    c: nst.IPv4Address = classno.field(default_factory=random_ipv4)
    d: list[str] = ["Foo", "Bar"]


t = SubClassno()
