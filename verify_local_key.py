
import firebase_admin
from firebase_admin import credentials
import os

try:
    cred = credentials.Certificate('serviceAccountKey.json')
    app = firebase_admin.initialize_app(cred)
    print("Local serviceAccountKey.json is VALID and loaded successfully.")
except Exception as e:
    print(f"Local serviceAccountKey.json is INVALID. Error: {e}")
