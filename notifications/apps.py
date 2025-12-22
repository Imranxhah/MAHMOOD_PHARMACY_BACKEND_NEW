import os
from django.apps import AppConfig
from django.conf import settings
import firebase_admin
from firebase_admin import credentials

class NotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notifications'

    def ready(self):
        import notifications.signals
        # Initialize Firebase Admin SDK
        cred_path = os.getenv('FIREBASE_CREDENTIALS_PATH', 'serviceAccountKey.json')
        # Ensure path is absolute if needed, or relative to manage.py
        # If it's in the root, 'serviceAccountKey.json' works.
        
        if not firebase_admin._apps:
            try:
                # Construct full path to be safe
                base_dir = settings.BASE_DIR
                full_cred_path = os.path.join(base_dir, cred_path)
                
                if os.path.exists(full_cred_path):
                    cred = credentials.Certificate(full_cred_path)
                    firebase_admin.initialize_app(cred)
                    print("Firebase Admin SDK initialized successfully.")
                else:
                    print(f"Warning: Firebase credentials not found at {full_cred_path}")
            except Exception as e:
                print(f"Error initializing Firebase: {e}")
