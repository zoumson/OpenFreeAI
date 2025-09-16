# Use official Python image
FROM python:3.11-slim

# Set workdir
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app code
COPY . .

# Set PYTHONPATH so 'server' is importable
ENV PYTHONPATH=/app

# Expose port (web will use it)
EXPOSE 5000

# Default command (can be overridden by docker-compose)
CMD ["python", "server/app.py"]
