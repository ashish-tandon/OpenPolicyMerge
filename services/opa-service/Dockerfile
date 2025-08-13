FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY start.sh .

# Make start script executable
RUN chmod +x start.sh

# Expose port 8181
EXPOSE 8181

# Set environment variables
ENV SERVICE_PORT=8181
ENV SERVICE_NAME=opa-service
ENV PYTHONPATH=/app/src

# Run the service
CMD ["./start.sh"]
