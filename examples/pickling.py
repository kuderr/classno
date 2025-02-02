import pickle
import classno


class SubClassno(classno.Classno):
    a: int = 1
    b: str = classno.field(default="foobar")
    d: list[str] = ["Foo", "Bar"]


t = SubClassno()
t2 = pickle.loads(pickle.dumps(t))
