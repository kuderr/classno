import copy

import classno


class SubClassno(classno.Classno):
    a: int = 1
    b: str = classno.field(default="foobar")
    d: list[str] = ["Foo", "Bar"]


t = SubClassno()
shallow = copy.copy(t)
deep = copy.deepcopy(t)
