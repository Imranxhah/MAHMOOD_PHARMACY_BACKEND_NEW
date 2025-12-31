
import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

with open('verification.txt', 'w', encoding='utf-8') as f:
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='marketing_feedback';")
            row = cursor.fetchone()
            if row:
                f.write("SUCCESS")
            else:
                f.write("FAILURE: Table not found")
    except Exception as e:
        f.write(f"ERROR: {e}")
