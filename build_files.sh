#!/bin/bash

# Build Script for Vercel

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Creating staticfiles directory..."
mkdir -p staticfiles_build/static

echo "Copying static files..."
cp -r staticfiles/* staticfiles_build/static/

# Collect static files
python manage.py collectstatic --noinput

# Make migrations
python manage.py makemigrations
python manage.py migrate

# Deactivate virtual environment
deactivate
