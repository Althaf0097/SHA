# Deployment Guide for Hospital Management System

## Prerequisites

1. Python 3.8 or higher
2. PostgreSQL 13 or higher
3. Domain name (for production)
4. SSL certificate (for HTTPS)
5. Linux server (recommended) or Windows server

## Step 1: Prepare the Environment

1. Create a new virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Linux/Mac
   .\venv\Scripts\activate  # On Windows
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Step 2: Configure Production Settings

1. Set environment variables:
   ```bash
   export DJANGO_SETTINGS_MODULE=hospital_management.settings_prod
   export DJANGO_SECRET_KEY='your-secure-secret-key'
   export DB_NAME='hospital_db'
   export DB_USER='your_db_user'
   export DB_PASSWORD='your_db_password'
   export DB_HOST='your_db_host'
   ```

2. Update `settings_prod.py` with your domain:
   ```python
   ALLOWED_HOSTS = ['your-domain.com']
   ```

## Step 3: Database Setup

1. Create PostgreSQL database:
   ```sql
   CREATE DATABASE hospital_db;
   ```

2. Apply migrations:
   ```bash
   python manage.py migrate
   ```

3. Create superuser:
   ```bash
   python manage.py createsuperuser
   ```

## Step 4: Static and Media Files

1. Collect static files:
   ```bash
   python manage.py collectstatic
   ```

2. Configure your web server to serve static and media files from their respective directories.

## Step 5: Web Server Setup (Using Gunicorn)

1. Install Gunicorn (already in requirements.txt)

2. Create a Gunicorn service file (on Linux):
   ```ini
   [Unit]
   Description=Hospital Management Gunicorn Daemon
   After=network.target

   [Service]
   User=your_user
   Group=your_group
   WorkingDirectory=/path/to/your/project
   ExecStart=/path/to/venv/bin/gunicorn --workers 3 --bind unix:/path/to/hospital_management.sock hospital_management.wsgi:application

   [Install]
   WantedBy=multi-user.target
   ```

## Step 6: Nginx Configuration

1. Install Nginx

2. Create Nginx configuration:
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location = /favicon.ico { access_log off; log_not_found off; }

       location /static/ {
           root /path/to/your/project;
       }

       location /media/ {
           root /path/to/your/project;
       }

       location / {
           include proxy_params;
           proxy_pass http://unix:/path/to/hospital_management.sock;
       }
   }
   ```

## Step 7: SSL Configuration

1. Install Certbot for SSL:
   ```bash
   sudo apt-get install certbot python3-certbot-nginx
   ```

2. Obtain SSL certificate:
   ```bash
   sudo certbot --nginx -d your-domain.com
   ```

## Step 8: Final Steps

1. Start Gunicorn service:
   ```bash
   sudo systemctl start gunicorn
   sudo systemctl enable gunicorn
   ```

2. Start Nginx:
   ```bash
   sudo systemctl start nginx
   sudo systemctl enable nginx
   ```

## Security Considerations

1. Keep `DEBUG = False` in production
2. Use strong, unique passwords
3. Regularly update dependencies
4. Configure proper backup systems
5. Monitor server logs
6. Set up proper firewall rules

## Maintenance

1. Regular backups:
   ```bash
   pg_dump hospital_db > backup.sql
   ```

2. Update dependencies:
   ```bash
   pip install -r requirements.txt --upgrade
   ```

3. Monitor logs:
   ```bash
   tail -f /path/to/your/project/logs/django.log
   ```

## Troubleshooting

1. Check logs for errors:
   - Nginx logs: `/var/log/nginx/error.log`
   - Gunicorn logs: `/var/log/gunicorn/error.log`
   - Application logs: `logs/django.log`

2. Common issues:
   - Static files not loading: Check STATIC_ROOT and nginx configuration
   - Database connection issues: Verify database credentials and firewall settings
   - 502 Bad Gateway: Check if Gunicorn is running

For additional support, refer to the Django deployment documentation or contact the development team.