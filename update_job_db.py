import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alumni_backend.settings')
django.setup()
from django.db import connection
try:
    with connection.cursor() as cursor:
        cursor.execute("ALTER TABLE portal_job ADD COLUMN company_name VARCHAR(200)")
        cursor.execute("ALTER TABLE portal_job ADD COLUMN location VARCHAR(200)")
        cursor.execute("ALTER TABLE portal_job ADD COLUMN job_type VARCHAR(50) DEFAULT 'FULL_TIME'")
        cursor.execute("ALTER TABLE portal_job ADD COLUMN poster_image VARCHAR(100)")
    print("Columns added successfully")
except Exception as e:
    print("Error or already added:", e)
