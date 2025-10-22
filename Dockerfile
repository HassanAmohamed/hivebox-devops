# Import Base Image Python-alpine
FROM python:3.11-alpine AS builder

# Set WorkDir
WORKDIR /app

# Install necessary build dependencies
RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev \
    postgresql-dev

# Copy the requirements to working directory
COPY requirements.txt .

# Install Python dependencies to the specified install prefix
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Start a new stage from the same base image for the final application
FROM python:3.11-alpine

# Set the working directory inside the container for the final image
WORKDIR /app

# Install the PostgreSQL client library
RUN apk add --no-cache libpq

# Copy installed Python packages from the builder stage
COPY --from=builder /install /usr/local

# Copy the rest of the application code into the container
COPY . .

# Clean up unnecessary files to reduce image size
RUN find . -name "*.pyc" -delete && \
    find . -name "__pycache__" -exec rm -rf {} + && \
    rm -rf -- .git* ./*.md ./*.yml discussion_board/tests

# Expose port 8000 for the application
EXPOSE 8000

# Create a non-root user for running the application
RUN adduser -D appuser

# Switch to the newly created non-root user
USER appuser

# Define the command to run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]