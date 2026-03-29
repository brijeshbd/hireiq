FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy and install requirements
COPY requirements.txt .

# Install in one layer — faster!
RUN pip install --no-cache-dir -r requirements.txt

# Copy code
COPY . .

CMD uvicorn api:app --host 0.0.0.0 --port ${PORT:-8000}