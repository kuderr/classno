#!/bin/bash

# Comprehensive test runner for classno
# This script runs all test suites and generates coverage reports

set -e  # Exit on any error

echo "🚀 Starting comprehensive test suite for classno..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Create results directory
mkdir -p test_results

# Run different test categories
print_status "Running unit tests..."
poetry run pytest tests/unit/ -v --junitxml=test_results/unit_tests.xml

print_status "Running integration tests..."
poetry run pytest tests/integration/ -v --junitxml=test_results/integration_tests.xml

print_status "Running edge case tests..."  
poetry run pytest tests/edge_cases/ -v --junitxml=test_results/edge_case_tests.xml

print_status "Running regression tests..."
poetry run pytest tests/regression/ -v --junitxml=test_results/regression_tests.xml

# Run all tests with coverage
print_status "Running full test suite with coverage..."
poetry run pytest tests/ \
    --cov=classno \
    --cov-report=html \
    --cov-report=term-missing \
    --cov-report=xml \
    --cov-fail-under=85 \
    --junitxml=test_results/all_tests.xml

# Generate coverage badge (if coverage-badge is installed)
if command -v coverage-badge &> /dev/null; then
    print_status "Generating coverage badge..."
    coverage-badge -o test_results/coverage.svg
fi

# Summary
print_status "Test results summary:"
echo "  - Unit tests: tests/unit/"
echo "  - Integration tests: tests/integration/" 
echo "  - Edge case tests: tests/edge_cases/"
echo "  - Regression tests: tests/regression/"
echo "  - Coverage report: htmlcov/index.html"
echo "  - Test results: test_results/"

print_success "All tests completed! ✅"

# Check if coverage threshold was met
if [ $? -eq 0 ]; then
    print_success "Coverage threshold met! ✅"
else
    print_warning "Coverage threshold not met - please add more tests ⚠️"
fi