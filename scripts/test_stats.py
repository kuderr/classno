#!/usr/bin/env python3
"""
Test statistics and reporting tool for classno.

Generates comprehensive statistics about the test suite.
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple
import ast

def count_lines_in_file(file_path: Path) -> int:
    """Count lines in a Python file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return len(f.readlines())
    except (UnicodeDecodeError, IOError):
        return 0

def count_test_functions(file_path: Path) -> int:
    """Count test functions in a Python file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        count = 0
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
                count += 1
        
        return count
    except (SyntaxError, UnicodeDecodeError, IOError):
        return 0

def count_test_classes(file_path: Path) -> int:
    """Count test classes in a Python file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        count = 0
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name.startswith('Test'):
                count += 1
        
        return count
    except (SyntaxError, UnicodeDecodeError, IOError):
        return 0

def analyze_test_directory(test_dir: Path) -> Dict[str, any]:
    """Analyze a test directory and return statistics."""
    stats = {
        'files': 0,
        'test_functions': 0,
        'test_classes': 0,
        'lines_of_code': 0,
        'file_details': []
    }
    
    if not test_dir.exists():
        return stats
    
    for file_path in test_dir.rglob('test_*.py'):
        if file_path.is_file():
            lines = count_lines_in_file(file_path)
            functions = count_test_functions(file_path)
            classes = count_test_classes(file_path)
            
            stats['files'] += 1
            stats['test_functions'] += functions
            stats['test_classes'] += classes
            stats['lines_of_code'] += lines
            
            stats['file_details'].append({
                'file': str(file_path.relative_to(test_dir.parent)),
                'lines': lines,
                'functions': functions,
                'classes': classes
            })
    
    return stats

def print_statistics():
    """Print comprehensive test statistics."""
    project_root = Path(__file__).parent.parent
    tests_dir = project_root / 'tests'
    
    print("🧪 Classno Test Suite Statistics")
    print("=" * 50)
    
    # Overall statistics
    total_stats = analyze_test_directory(tests_dir)
    
    print(f"📊 Overall Test Suite:")
    print(f"  Total test files: {total_stats['files']}")
    print(f"  Total test functions: {total_stats['test_functions']}")
    print(f"  Total test classes: {total_stats['test_classes']}")
    print(f"  Total lines of test code: {total_stats['lines_of_code']}")
    print()
    
    # Category breakdown
    categories = {
        'Unit Tests': 'unit',
        'Integration Tests': 'integration', 
        'Edge Case Tests': 'edge_cases',
        'Regression Tests': 'regression'
    }
    
    print("📁 Test Categories:")
    for category_name, category_dir in categories.items():
        cat_stats = analyze_test_directory(tests_dir / category_dir)
        print(f"  {category_name}:")
        print(f"    Files: {cat_stats['files']}")
        print(f"    Functions: {cat_stats['test_functions']}")
        print(f"    Classes: {cat_stats['test_classes']}")
        print(f"    Lines: {cat_stats['lines_of_code']}")
        print()
    
    # File details
    print("📄 Test File Details:")
    all_files = sorted(total_stats['file_details'], key=lambda x: x['functions'], reverse=True)
    
    print(f"{'File':<50} {'Lines':<8} {'Funcs':<8} {'Classes':<8}")
    print("-" * 74)
    
    for file_info in all_files[:20]:  # Show top 20 files
        print(f"{file_info['file']:<50} {file_info['lines']:<8} {file_info['functions']:<8} {file_info['classes']:<8}")
    
    if len(all_files) > 20:
        print(f"... and {len(all_files) - 20} more files")
    
    print()
    
    # Phase 2 specific statistics
    phase2_files = [f for f in all_files if any(name in f['file'] for name in [
        'mutable_defaults', 'casting_returns', 'feature_combinations', 
        'inheritance', 'optional_types', 'union_types', 'nested_structures', 
        'bug_fixes'
    ])]
    
    if phase2_files:
        print("🚀 Phase 2 Test Suite (Day 4-5):")
        phase2_functions = sum(f['functions'] for f in phase2_files)
        phase2_lines = sum(f['lines'] for f in phase2_files)
        
        print(f"  New test files: {len(phase2_files)}")
        print(f"  New test functions: {phase2_functions}")
        print(f"  New lines of test code: {phase2_lines}")
        
        print(f"\n  Breakdown:")
        for file_info in phase2_files:
            print(f"    {file_info['file']}: {file_info['functions']} functions, {file_info['lines']} lines")
    
    print()
    print("✅ Test suite analysis complete!")

if __name__ == "__main__":
    print_statistics()