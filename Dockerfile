# Use Python 3.9 base image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire app directory into Docker image
COPY . .

# Expose port 5000
EXPOSE 5000

# Command to run the Flask application
CMD ["python", "app.py"]

