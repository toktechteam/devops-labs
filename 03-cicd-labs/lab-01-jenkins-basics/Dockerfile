# Multi-stage Dockerfile for CI/CD demo application
FROM python:3.11-slim AS builder

WORKDIR /build

# Copy and install dependencies
COPY src/requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Run tests in build stage
FROM python:3.11-slim AS tester

WORKDIR /app

# Copy test requirements
COPY tests/requirements-test.txt .
RUN pip install --no-cache-dir -r requirements-test.txt

# Copy application and tests
COPY src/ ./src/
COPY tests/ ./tests/

# Copy dependencies from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Run tests
RUN python -m pytest tests/ -v

# Final production image
FROM python:3.11-slim

# Build arguments for versioning
ARG BUILD_NUMBER=0
ARG GIT_COMMIT=unknown
ARG APP_VERSION=1.0.0

# Create non-root user
RUN groupadd -r appuser && \
    useradd -r -g appuser -d /app -s /sbin/nologin appuser

WORKDIR /app

# Install curl for health checks
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# Copy dependencies from builder
COPY --from=builder /root/.local /usr/local

# Copy application code
COPY --chown=appuser:appuser src/app.py .
COPY --chown=appuser:appuser src/requirements.txt .

# Set environment variables
ENV BUILD_NUMBER=${BUILD_NUMBER} \
    GIT_COMMIT=${GIT_COMMIT} \
    APP_VERSION=${APP_VERSION} \
    ENVIRONMENT=production \
    PORT=5000

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

EXPOSE 5000

# Run with gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "30", "app:app"]
