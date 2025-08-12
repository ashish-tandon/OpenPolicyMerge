#!/bin/bash
echo "🔧 Setting up development environment..."

# Install development dependencies
source venv/bin/activate
pip install black ruff mypy pre-commit

# Setup pre-commit hooks
pre-commit install

echo "✅ Development environment setup completed"
echo "Available commands:"
echo "  black .          - Format code"
echo "  ruff check .     - Lint code"
echo "  mypy src/        - Type check"
echo "  pre-commit run   - Run all checks"
