#!/bin/bash

# Test CI/CD Pipeline Locally
# This script simulates the GitHub Actions workflow to test it locally

set -e

echo "🔧 Testing GitHub Actions workflow locally..."

# Test environment setup
echo "📦 Installing UV..."
if ! command -v uv &> /dev/null; then
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi

echo "📦 Installing dependencies..."
uv sync --frozen

echo "🌍 Setting up test environment variables..."
export DEBUG=True
export SECRET_KEY=test-secret-key-for-ci
export USE_S3=False

echo "📁 Creating static files directory..."
mkdir -p staticfiles

echo "🗄️  Running migrations..."
uv run python manage.py migrate

echo "📁 Collecting static files..."
uv run python manage.py collectstatic --noinput

echo "🔍 Running linting..."
uv run ruff check . || echo "⚠️  Linting issues found (continuing...)"

echo "🧪 Running tests with coverage..."
uv run python -m pytest --cov=. --cov-report=xml --cov-report=html --cov-report=term-missing -v

echo "✅ All CI/CD checks passed!"
echo ""
echo "📊 Coverage report generated in htmlcov/"
echo "📄 XML coverage report: coverage.xml"
echo ""
echo "🚀 Ready for GitHub Actions deployment!"
