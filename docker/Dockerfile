# Multi-stage Dockerfile for Django Application
# Optimized for production use with PostGIS support

# ============== BUILD STAGE ==============
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gdal-bin \
    libgdal-dev \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install gunicorn

# ============== RUNTIME STAGE ==============
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies (minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    gdal-bin \
    postgresql-client \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Set environment variables
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Create non-root user for security
RUN groupadd -r django && useradd -r -g django django

# Copy application code
COPY --chown=django:django . .

# Create necessary directories
RUN mkdir -p /app/staticfiles /app/media /app/logs && \
    chown -R django:django /app

# Switch to non-root user
USER django

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Default command
CMD ["/bin/sh", "-c", "python manage.py collectstatic --noinput && gunicorn -w 4 -b 0.0.0.0:8000 --access-logfile - --error-logfile - --log-level info irish_civil_war_project.wsgi:application"]

# Labels
LABEL maintainer="Oisin Cruise <oisincruise@gmail.com>" \
      description="Django application for Irish Civil War LBS" \
      version="1.0.0"
