import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alumni_backend.settings')
django.setup()
from django.db import connection
try:
    with connection.cursor() as cursor:
        cursor.execute("ALTER TABLE portal_post ADD COLUMN poster_image VARCHAR(100)")
        cursor.execute("ALTER TABLE portal_event ADD COLUMN poster_image VARCHAR(100)")
    print("Columns added successfully")
except Exception as e:
    print("Error or already added:", e)
