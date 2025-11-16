# Classno

[![pypi](https://img.shields.io/pypi/v/classno.svg)](https://pypi.org/project/classno/)
[![downloads](https://static.pepy.tech/badge/classno)](https://www.pepy.tech/projects/classno)
[![downloads](https://static.pepy.tech/badge/classno/month)](https://www.pepy.tech/projects/classno)
[![versions](https://img.shields.io/pypi/pyversions/classno.svg)](https://github.com/kuderr/classno)
[![license](https://img.shields.io/github/license/kuderr/classno.svg)](https://github.com/kuderr/classno/blob/master/LICENSE)
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/kuderr/classno)

Classno is a lightweight and extensible Python library for data modeling, schema definition, and validation. It provides a clean and intuitive way to define data classes with various features like type validation, immutability, private fields, and automatic type casting.

## Key Features

- Type hints validation
- Immutable objects
- Private fields
- Automatic type casting
- Customizable comparison behavior
- Default values and factory functions
- Nested object support
- Slots optimization
- Rich comparison methods

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

## Customization

### Custom Comparison Keys

```python
class CustomCompare(Classno):
    __hash_keys__ = {"id"}  # Keys used for hashing
    __eq_keys__ = {"id", "name"}  # Keys used for equality comparison
    __order_keys__ = {"name"}  # Keys used for ordering

    id: int
    name: str
    description: str
```

## Best Practices

1. Use type hints for all fields
2. Enable appropriate features based on your needs
3. Use `field()` for complex field configurations
4. Consider using `Features.SLOTS` for better memory usage
5. Enable validation when type safety is important

## Error Handling

The library raises appropriate exceptions for:

- Type validation errors
- Missing required fields
- Immutability violations
- Invalid field access
- Incorrect feature combinations

# Authors

- Dmitriy Kudryavtsev - author - [kuderr](https://github.com/kuderr)
