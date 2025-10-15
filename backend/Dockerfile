FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Nebula binaries
RUN wget https://github.com/slackhq/nebula/releases/download/v1.8.2/nebula-linux-amd64.tar.gz \
    && tar -xzf nebula-linux-amd64.tar.gz \
    && mv nebula /usr/local/bin/ \
    && mv nebula-cert /usr/local/bin/ \
    && rm nebula-linux-amd64.tar.gz \
    && chmod +x /usr/local/bin/nebula /usr/local/bin/nebula-cert

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /etc/nebula /tmp/nebula-certs

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]