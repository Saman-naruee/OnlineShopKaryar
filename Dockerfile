# ./Dockerfile
# To create an image: docker build -t IMAGE_NAME .
# To create a container from that image: docker run -d -p 8000:8000 --name onlineshop-app IMAGE_NAME
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create directory for media files
RUN mkdir -p /app/media

# Collect static files (for Django)
RUN python manage.py collectstatic --no-input
