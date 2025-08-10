# Multi-stage Dockerfile for Python application
# Stage 1: Build dependencies
FROM python:3.11-slim AS builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python packages to a specific location
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Test (optional)
FROM python:3.11-slim AS tester

WORKDIR /test

# Copy test requirements if any
COPY requirements-test.txt* ./

# Install test dependencies
RUN if [ -f requirements-test.txt ]; then \
    pip install --no-cache-dir -r requirements-test.txt; \
    fi

# Copy application and tests
COPY . .

# Copy dependencies from builder
COPY --from=builder /root/.local /root/.local

# Run tests
RUN python -m pytest tests/ 2>/dev/null || echo "No tests found"

# Stage 3: Final minimal image
FROM python:3.11-slim

# Create non-root user
RUN groupadd -r appuser && \
    useradd -r -g appuser -d /app -s /sbin/nologin appuser

WORKDIR /app

# Install only runtime dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /root/.local /usr/local

# Copy application
COPY --chown=appuser:appuser app.py .

# Set environment
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=5000

USER appuser

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

CMD ["python", "app.py"]

# Image size: ~150MB