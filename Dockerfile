# Stage 1: Build environment
FROM python:3.9-alpine as builder

# Install build dependencies
RUN apk add --no-cache \
    gcc \
    musl-dev \
    python3-dev \
    libffi-dev \
    openssl-dev \
    cargo

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime environment
FROM python:3.9-alpine

# Install runtime dependencies
RUN apk add --no-cache libstdc++

WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local
COPY --from=builder /app/requirements.txt .

# Ensure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY . .

# Security best practices
RUN adduser -D myuser && \
    chown -R myuser:myuser /app
USER myuser

# Lint check (optional - remove for production)
RUN pip install pylint && \
    pylint --disable=R,C,W1203,W1202,W0613 api/ config/ && \
    pip uninstall -y pylint

# Collect static files
RUN python manage.py collectstatic --noinput

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/version || exit 1

# Expose port
EXPOSE 8000

# Run application with optimized Gunicorn config
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi:application"]