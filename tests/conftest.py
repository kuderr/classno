"""
Pytest configuration and test utilities for classno tests.
"""

import sys
from pathlib import Path

import pytest


# Add the project root to Python path so we can import classno
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Common test fixtures and utilities
@pytest.fixture
def sample_data():
    """Sample data for testing."""
    return {
        'strings': ['hello', 'world', 'test'],
        'integers': [1, 2, 3, 42, -5],
        'floats': [1.0, 2.5, 3.14, -1.5],
        'nested_list': [[1, 2], [3, 4], [5, 6]],
        'nested_dict': {'a': {'x': 1, 'y': 2}, 'b': {'x': 3, 'y': 4}},
        'mixed_types': [1, 'hello', 3.14, True, None],
    }

@pytest.fixture
def performance_data():
    """Large data sets for performance testing."""
    return {
        'large_list': list(range(1000)),
        'large_dict': {f'key_{i}': f'value_{i}' for i in range(1000)},
        'deeply_nested': {'level_0': {'level_1': {'level_2': {'level_3': 'deep_value'}}}},
    }

# Test utilities
class TestHelpers:
    """Helper methods for testing."""

    @staticmethod
    def assert_independent_objects(obj1, obj2, mutable_attr_name):
        """Assert that two objects have independent mutable attributes."""
        attr1 = getattr(obj1, mutable_attr_name)
        attr2 = getattr(obj2, mutable_attr_name)

        # They should not be the same object
        assert attr1 is not attr2, f"Objects share the same {mutable_attr_name} instance"

        # Modifying one should not affect the other
        if isinstance(attr1, list):
            original_length = len(attr2)
            attr1.append('test_independence')
            assert len(attr2) == original_length, f"Modifying obj1.{mutable_attr_name} affected obj2"
        elif isinstance(attr1, dict):
            original_keys = set(attr2.keys())
            attr1['test_independence'] = True
            assert set(attr2.keys()) == original_keys, f"Modifying obj1.{mutable_attr_name} affected obj2"
        elif isinstance(attr1, set):
            original_size = len(attr2)
            attr1.add('test_independence')
            assert len(attr2) == original_size, f"Modifying obj1.{mutable_attr_name} affected obj2"

    @staticmethod
    def create_test_classes():
        """Create various test classes for complex scenarios."""
        from typing import Dict
        from typing import List
        from typing import Optional
        from typing import Union

        from classno import Classno
        from classno import Features
        from classno import field

        class BasicClass(Classno):
            __features__ = Features.EQ
            name: str
            value: int

        class ValidationClass(Classno):
            __features__ = Features.VALIDATION | Features.EQ
            name: str
            count: int
            items: List[str] = field(default_factory=list)

        class CastingClass(Classno):
            __features__ = Features.LOSSY_AUTOCAST | Features.EQ
            name: str
            numbers: List[int] = field(default_factory=list)
            mapping: Dict[str, int] = field(default_factory=dict)

        class ComplexClass(Classno):
            __features__ = Features.EQ | Features.ORDER | Features.HASH
            __eq_keys__ = ('id',)
            __order_keys__ = ('name', 'priority')
            __hash_keys__ = ('id',)
            id: int
            name: str
            priority: int
            data: Optional[Dict[str, Union[int, str]]] = None

        return {
            'basic': BasicClass,
            'validation': ValidationClass,
            'casting': CastingClass,
            'complex': ComplexClass,
        }

# Make helpers available at module level
helpers = TestHelpers()
