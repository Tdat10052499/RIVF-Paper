FROM python:3.11-slim

WORKDIR /workspace

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir \
    torch==2.14.0 \
    torchvision \
    pillow \
    numpy

# Copy project files
COPY . /workspace

CMD ["bash"]
