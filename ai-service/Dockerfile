# --- Stage 1: Build Stage ---
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build tools for C-extensions (scipy/numpy need this)
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install CPU versions specifically to save space
RUN pip install --user --no-cache-dir -r requirements.txt

# --- Stage 2: Final Runtime ---
FROM python:3.11-slim

WORKDIR /app

# Copy only the installed packages from the builder
COPY --from=builder /root/.local /root/.local
COPY . .

# Set paths so Python finds the local installs
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONPATH=/root/.local/lib/python3.11/site-packages

# Optimization: Tell Transformers/Torch not to look for a GPU
ENV CUDA_VISIBLE_DEVICES=""

EXPOSE $PORT

CMD ["sh", "-c", "uvicorn api:app --host 0.0.0.0 --port ${PORT:-8000}"]