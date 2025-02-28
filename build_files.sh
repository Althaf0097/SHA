# Build Script for Vercel

# Create python virtual environment
python -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install python dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput

# Make migrations
python manage.py makemigrations
python manage.py migrate

# Deactivate virtual environment
deactivate