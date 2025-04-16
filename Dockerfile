FROM python:3.11-slim

WORKDIR /app

# Install minimal dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables to ensure Python produces readable output
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Copy package files
COPY pyproject.toml ./
COPY README.md ./
COPY main.py ./
COPY src ./src

# Install dependencies using pip
RUN pip install --no-cache-dir -e .

# This image only supports STDIO mode (for Claude Desktop)
CMD ["python", "main.py"] 