FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY start.sh .

# Make startup script executable
RUN chmod +x start.sh

# Create necessary directories
RUN mkdir -p logs staticfiles media

# Expose port
EXPOSE 9022

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:9022/ || exit 1

# Start the application
CMD ["./start.sh"]
