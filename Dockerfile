# Use official Python image
FROM python:3.11-slim

# Set workdir
WORKDIR /app

# Copy requirements first (caching layer)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install dependencies for dockerize download
RUN apt-get update && apt-get install -y wget tar curl jq && rm -rf /var/lib/apt/lists/*

# Automatically fetch latest dockerize release
RUN LATEST=$(curl -s https://api.github.com/repos/jwilder/dockerize/releases/latest \
              | jq -r '.tag_name') \
    && wget https://github.com/jwilder/dockerize/releases/download/${LATEST}/dockerize-linux-amd64-${LATEST}.tar.gz \
    && tar -C /usr/local/bin -xzvf dockerize-linux-amd64-${LATEST}.tar.gz \
    && rm dockerize-linux-amd64-${LATEST}.tar.gz

# Copy the rest of the code
COPY . .

# Create a non-root user for security
RUN useradd -ms /bin/bash adama

# # Create instance folder and fix permissions
# RUN mkdir -p /app/server/instance && chown -R adama:adama /app/server/instance

# Switch to non-root user
USER adama

# Set PYTHONPATH so 'server' is importable
ENV PYTHONPATH=/app

# Expose port (web will use it)
EXPOSE 5000

# Entrypoint is handled by docker-compose command
CMD ["sh", "-c", "echo 'Container started'"]
