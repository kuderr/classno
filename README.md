# Classno

[![pypi](https://img.shields.io/pypi/v/classno.svg)](https://pypi.org/project/classno/)
[![downloads](https://static.pepy.tech/badge/classno)](https://www.pepy.tech/projects/classno)
[![downloads](https://static.pepy.tech/badge/classno/month)](https://www.pepy.tech/projects/classno)
[![versions](https://img.shields.io/pypi/pyversions/classno.svg)](https://github.com/kuderr/classno)
[![license](https://img.shields.io/github/license/kuderr/classno.svg)](https://github.com/kuderr/classno/blob/master/LICENSE)
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/kuderr/classno)

Classno is a lightweight and extensible Python library for data modeling, schema definition, and validation. It provides a clean and intuitive way to define data classes with various features like type validation, immutability, private fields, and automatic type casting.

## Key Features

- **Type hints validation** - Runtime type checking for all fields
- **Immutable objects** - Create frozen, hashable instances
- **Private fields** - Write-once, read-only field access patterns
- **Automatic type casting** - Lossy autocast between compatible types
- **Customizable comparison** - Control equality, hashing, and ordering behavior
- **Default values and factories** - Safe handling of mutable defaults
- **Nested object support** - Deep validation and casting of complex structures
- **Slots optimization** - Reduced memory footprint
- **Rich comparison methods** - Full ordering support
- **Union and Optional types** - First-class support for `Optional[T]` and `Union[T1, T2]`
- **Extended collection types** - Support for `frozenset`, `deque`, `defaultdict`, and more

## Installation

```bash
pip install classno
```

## Basic Usage

### Simple Data Class

```python
from classno import Classno, field

class User(Classno):
    name: str
    age: int = 0
    email: str = field(default="")

# Create an instance
user = User(name="John", age=30)
```

### Features Configuration

Features can be enabled by setting the `__features__` class attribute:

```python
from classno import Classno, Features

class Config(Classno):
    __features__ = Features.VALIDATION | Features.FROZEN

    host: str
    port: int = 8080
```

Available features:

- `Features.EQ` - Enable equality comparison
- `Features.ORDER` - Enable ordering operations
- `Features.HASH` - Make instances hashable
- `Features.SLOTS` - Use slots for memory optimization
- `Features.FROZEN` - Make instances immutable
- `Features.PRIVATE` - Enable private field access
- `Features.VALIDATION` - Enable type validation
- `Features.LOSSY_AUTOCAST` - Enable automatic type casting

### Field Configuration

Fields can be configured using the `field()` function:

```python
from classno import Classno, field
from datetime import datetime

class Post(Classno):
    title: str
    content: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    metadata: dict = field(default_factory=dict, metadata={"indexed": True})
```

**Important:** Always use `default_factory` for mutable defaults (list, dict, set) to avoid shared state issues:

```python
# ❌ WRONG - This will raise an error
class Wrong(Classno):
    tags: list = []

# ✅ CORRECT - Use default_factory
class Correct(Classno):
    tags: list = field(default_factory=list)
```

### Type Validation

```python
class ValidatedModel(Classno):
    __features__ = Features.VALIDATION

    numbers: list[int]
    mapping: dict[str, float]

# This will raise TypeError if types don't match
model = ValidatedModel(
    numbers=[1, 2, 3],
    mapping={"a": 1.0, "b": 2.0}
)
```

#### Optional and Union Types

Full support for `Optional` and `Union` types with proper validation:

```python
from typing import Optional, Union

class FlexibleModel(Classno):
    __features__ = Features.VALIDATION

    # Optional field - can be None
    optional_name: Optional[str] = None

    # Union type - can be str or int
    identifier: Union[str, int]

    # Complex unions
    data: Union[list[str], dict[str, int], None] = None

model = FlexibleModel(optional_name=None, identifier=42)
```

#### Extended Collection Types

Support for Python's extended collection types:

```python
from collections import deque, defaultdict, Counter
from typing import Optional

class AdvancedCollections(Classno):
    __features__ = Features.VALIDATION | Features.LOSSY_AUTOCAST

    # Immutable set
    unique_ids: frozenset[int] = field(default_factory=frozenset)

    # Double-ended queue
    history: deque[str] = field(default_factory=deque)

    # Dict with default values
    counters: defaultdict[str, int] = field(
        default_factory=lambda: defaultdict(int)
    )

    # Counter for frequency tracking
    word_counts: Counter[str] = field(default_factory=Counter)
```

### Immutable Objects

```python
class ImmutableConfig(Classno):
    __features__ = Features.IMMUTABLE  # Combines FROZEN, SLOTS, and HASH

    host: str
    port: int = 8080

config = ImmutableConfig(host="localhost")
# Attempting to modify will raise an exception
config.port = 9000  # Raises Exception
```

### Private Fields

```python
class PrivateFields(Classno):
    __features__ = Features.PRIVATE

    name: str
    secret: str  # Can only be accessed with _secret prefix for rw, secret for ro

obj = PrivateFields(name="public")
obj._secret = "hidden"  # OK
obj.secret  # OK
obj.secret = "hidden"  # Raises Exception
```

### Nested Objects

```python
class Address(Classno):
    street: str
    city: str

class Person(Classno):
    name: str
    address: Address

# Create nested structure
person = Person(
    name="John",
    address=Address(street="123 Main St", city="Boston")
)
```

### Automatic Type Casting

Enable automatic type conversion with `LOSSY_AUTOCAST`:

```python
class AutoCastModel(Classno):
    __features__ = Features.LOSSY_AUTOCAST

    count: int
    price: float
    active: bool

# Automatic casting from compatible types
model = AutoCastModel(
    count="42",      # str → int
    price="19.99",   # str → float
    active="true"    # str → bool
)
# model.count == 42 (int)
# model.price == 19.99 (float)
# model.active == True (bool)
```

### Combining Features

Features can be combined for powerful data modeling:

```python
class RobustModel(Classno):
    # First cast, then validate
    __features__ = Features.LOSSY_AUTOCAST | Features.VALIDATION | Features.FROZEN

    user_id: int
    tags: list[str] = field(default_factory=list)

# This works: "42" is cast to 42, validated, then frozen
model = RobustModel(user_id="42", tags=["python", "classno"])
```

**Feature execution order:**

1. `LOSSY_AUTOCAST` - Values are automatically cast to target types
2. `VALIDATION` - Type validation is performed on cast values
3. `FROZEN` - Object becomes immutable after validation

## Customization

### Custom Comparison Keys

Control which fields participate in equality, hashing, and ordering:

```python
class CustomCompare(Classno):
    __features__ = Features.EQ | Features.HASH | Features.ORDER

    # Use tuples for ordered keys (order matters for comparison)
    __hash_keys__ = ("id",)              # Only id used for hashing
    __eq_keys__ = ("id", "name")         # id and name for equality
    __order_keys__ = ("priority", "name")  # Sort by priority, then name

    id: int
    name: str
    priority: int = 0
    description: str = ""

# Two objects are equal if id and name match
obj1 = CustomCompare(id=1, name="A", description="First")
obj2 = CustomCompare(id=1, name="A", description="Second")
assert obj1 == obj2  # True - description is ignored

# Ordering uses priority first, then name
items = [
    CustomCompare(id=1, name="B", priority=2),
    CustomCompare(id=2, name="A", priority=1),
]
sorted_items = sorted(items)  # Sorted by priority, then name
```

## Best Practices

1. **Use type hints for all fields** - Enables validation and better IDE support
2. **Use `default_factory` for mutable defaults** - Always use `field(default_factory=list)` instead of `field(default=[])`
3. **Enable appropriate features** - Only enable features you need (e.g., `VALIDATION` in development, `FROZEN` for config)
4. **Use `Features.SLOTS`** - Reduces memory usage by ~40% for classes with many instances
5. **Combine `LOSSY_AUTOCAST` with `VALIDATION`** - Cast first, then validate for robust data handling
6. **Use tuples for comparison keys** - `__eq_keys__ = ("id", "name")` not `["id", "name"]`
7. **Leverage `Optional` and `Union`** - Use proper type hints for flexible APIs

## Error Handling

Classno provides clear, actionable error messages:

```python
# Validation error
class Model(Classno):
    __features__ = Features.VALIDATION
    age: int

try:
    Model(age="not a number")
except ValidationError as e:
    # "Validation error for field 'age': expected int, got 'not a number' of type str"
    pass

# Mutable default error
try:
    class Wrong(Classno):
        tags: list = []  # ❌ Error at class definition time
except ValueError as e:
    # "Mutable default values are not allowed. Found list [].
    #  Use default_factory=lambda: [] instead to avoid shared state issues."
    pass

# Frozen modification error
class Frozen(Classno):
    __features__ = Features.FROZEN
    value: int

obj = Frozen(value=42)
try:
    obj.value = 100
except AttributeError as e:
    # "Cannot modify attributes of frozen class Frozen"
    pass
```

The library raises appropriate exceptions for:

- **ValidationError** - Type validation failures
- **TypeError** - Type mismatch during casting or validation
- **ValueError** - Invalid field configurations (e.g., mutable defaults)
- **AttributeError** - Immutability violations (FROZEN), invalid field access (PRIVATE)

## Advanced Usage

### Inheritance

Features and fields are properly inherited:

```python
class BaseModel(Classno):
    __features__ = Features.VALIDATION
    id: int

class UserModel(BaseModel):
    # Inherits VALIDATION feature and id field
    name: str
    email: str

user = UserModel(id=1, name="John", email="john@example.com")
```

### Serialization

Convert objects to dictionaries for JSON serialization:

```python
class User(Classno):
    name: str
    age: int

user = User(name="John", age=30)
data = user.as_dict()  # {"name": "John", "age": 30}
```

### Copying

Objects support both shallow and deep copying:

```python
import copy

original = User(name="John", age=30)
shallow = copy.copy(original)
deep = copy.deepcopy(original)
```

## Testing

Run the comprehensive test suite:

```bash
# Install development dependencies
poetry install

# Run all tests
poetry run poe tests

# Run fast tests (skip slow tests)
poetry run poe test-fast

# Run with coverage
poetry run poe test-all

# Run specific test categories
poetry run poe test-unit          # Unit tests
poetry run poe test-integration   # Integration tests
poetry run poe test-edge-cases    # Edge case tests
```

# Authors

- Dmitriy Kudryavtsev - author - [kuderr](https://github.com/kuderr)
