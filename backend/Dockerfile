# Use Python 3.11 slim image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libmagic1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    mv /root/.cargo/bin/uv /usr/local/bin/uv || \
    mv /root/.local/bin/uv /usr/local/bin/uv || \
    find /root -name uv -type f 2>/dev/null | head -1 | xargs -I {} cp {} /usr/local/bin/uv

# Set work directory
WORKDIR /app

# Copy project files
COPY pyproject.toml uv.lock ./
COPY . .

# Install dependencies
RUN uv sync --frozen

# Create logs directory
RUN mkdir -p logs

# Collect static files (if needed)
RUN uv run python manage.py collectstatic --noinput || true

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/schema/ || exit 1

# Run the application with Gunicorn
CMD ["uv", "run", "gunicorn", "--config", "gunicorn.conf.py", "core.wsgi:application"]
