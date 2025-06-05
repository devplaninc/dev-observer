# Server Backend Dockerfile
# Multi-stage build for minimal image size

# Build stage
FROM python:3.13-slim AS build

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy the entire server directory
COPY server/ ./

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir uv && \
    uv pip install --system .

# Production stage
FROM python:3.13-slim

WORKDIR /app

# Copy only necessary files from build stage
COPY --from=build /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=build /usr/local/bin /usr/local/bin

# Copy application code
COPY server/ ./server/

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose the port the server runs on
EXPOSE 8090

# Run the server
CMD ["python", "-m", "dev_observer.server.main"]
