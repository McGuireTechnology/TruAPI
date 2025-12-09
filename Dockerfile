# Build stage
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Copy dependency files first (for better caching)
COPY pyproject.toml ./

# Install Poetry
RUN pip install --no-cache-dir poetry==1.8.3

# Configure Poetry to not create virtual environment
RUN poetry config virtualenvs.create false

# Install dependencies (Poetry will create lock file if missing)
RUN poetry install --only main --no-interaction --no-ansi --no-root

# Runtime stage
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY api ./api

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')"

# Run application
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8080"]
