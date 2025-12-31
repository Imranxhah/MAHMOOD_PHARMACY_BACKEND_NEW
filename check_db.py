
import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

with connection.cursor() as cursor:
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    print("Tables found:", tables)
    if 'marketing_feedback' in tables:
        print("SUCCESS: marketing_feedback table exists.")
    else:
        print("FAILURE: marketing_feedback table does NOT exist.")
