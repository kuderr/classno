import random

from netsome import types as nst

import classno


def random_asn():
    number = random.randint(65000, 65535)
    return nst.ASN(number)


class Base(classno.Classno):
    __features__ = (
        classno.Features.DEFAULT
        | classno.Features.LOSSY_AUTOCAST
        | classno.Features.VALIDATION
        | classno.Features.PRIVATE
    )


class BGP(Base):
    asn: nst.ASN = classno.field(default_factory=random_asn)


class Switch(Base):
    hostname: str = ""
    bgp: BGP | None


sw = Switch(hostname="c-test-leaf1", bgp=BGP())
