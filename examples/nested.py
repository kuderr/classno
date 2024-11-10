import random

from netsome import types as nst

import classno


def random_asn():
    number = random.randint(65000, 65535)
    return nst.ASN(number)


class BGP(classno.Classno):
    asn: nst.ASN = classno.field(default_factory=random_asn)


class Switch(classno.Classno):
    hostname: str = ""
    bgp: BGP | None


t = Switch(hostname="c-test-leaf1", bgp=BGP())
