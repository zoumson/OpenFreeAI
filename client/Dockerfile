# Base image with Python
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Copy requirements first for caching
COPY requirements.txt .


RUN pip uninstall -y gradio && pip install gradio==4.44.1

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy everything in the client folder into /app
COPY . .

# Expose port for Gradio
EXPOSE 7860

# Command to run the UI client
CMD ["python", "ui_client.py"]
