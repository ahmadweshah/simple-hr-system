#!/bin/bash

# Simple HR System Docker Runner
# Usage: ./run.sh [dev|prod|build|clean]

set -e

case "${1:-dev}" in
    "dev")
        echo "🚀 Starting development environment..."
        docker-compose up --build
        ;;
    "prod")
        echo "🚀 Starting production environment..."
        docker-compose -f docker-compose.prod.yml up --build
        ;;
    "build")
        echo "🔨 Building Docker image..."
        docker build -t simple-hr-system .
        ;;
    "clean")
        echo "🧹 Cleaning up Docker containers and images..."
        docker-compose down -v --remove-orphans
        docker-compose -f docker-compose.prod.yml down -v --remove-orphans
        docker system prune -f
        ;;
    "test")
        echo "🧪 Running tests in Docker..."
        docker build -t simple-hr-system-test .
        docker run --rm simple-hr-system-test uv run python -m pytest
        ;;
    "test-local")
        echo "🧪 Running tests locally..."
        uv run python -m pytest
        ;;
    "test-coverage")
        echo "🧪 Running tests with coverage locally..."
        uv run python -m pytest --cov=. --cov-report=html --cov-report=term-missing
        ;;
    *)
        echo "Usage: $0 [dev|prod|build|clean|test|test-local|test-coverage]"
        echo ""
        echo "Commands:"
        echo "  dev           - Start development environment with Django dev server"
        echo "  prod          - Start production environment with Gunicorn"
        echo "  build         - Build Docker image only"
        echo "  clean         - Clean up Docker containers and images"
        echo "  test          - Run tests in Docker container"
        echo "  test-local    - Run tests locally with UV"
        echo "  test-coverage - Run tests with coverage locally"
        exit 1
        ;;
esac
