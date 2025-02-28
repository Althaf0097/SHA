# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Create directory for static files
RUN mkdir -p /app/staticfiles
RUN chmod -R 755 /app/staticfiles

# Collect static files
RUN python manage.py collectstatic --noinput

# Create logs directory
RUN mkdir -p /app/logs

# Set production settings
ENV DJANGO_SETTINGS_MODULE=hospital_management.settings_prod

# Run gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "hospital_management.wsgi:application"]
