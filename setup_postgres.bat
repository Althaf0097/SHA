@echo off
echo Installing PostgreSQL...
echo Please follow these steps:

echo 1. Download PostgreSQL 13 from: https://www.enterprisedb.com/downloads/postgres-postgresql-downloads
echo 2. Run the installer
echo 3. Use these settings during installation:
echo    - Installation Directory: C:\Program Files\PostgreSQL\13
echo    - Data Directory: C:\Program Files\PostgreSQL\13\data
echo    - Password: postgres
echo    - Port: 5432
echo    - Locale: Default

echo After installation:
echo 1. Open pgAdmin 4
echo 2. Create a new database named 'hospital_db'
echo 3. Make sure the postgres service is running

echo To verify installation, open a new command prompt and type:
echo psql -U postgres -d hospital_db

pause
