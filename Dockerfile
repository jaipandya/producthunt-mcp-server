FROM python:3.11-slim

WORKDIR /app

# Install minimal dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables to ensure Python produces readable output
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Create a non-root user
RUN adduser --disabled-password --gecos '' mcp_user

# Copy package files
COPY pyproject.toml ./
COPY README.md ./
COPY main.py ./
COPY src ./src

# Install dependencies using pip
RUN pip install --no-cache-dir -e .

# Change ownership to the non-root user
RUN chown -R mcp_user:mcp_user /app

# Switch to non-root user
USER mcp_user

# Health check (will confirm Python is working)
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD python -c "import sys; sys.exit(0 if 'PRODUCT_HUNT_TOKEN' in __import__('os').environ else 1)"

# This image only supports STDIO mode (for Claude Desktop and similar clients)
CMD ["python", "main.py"]