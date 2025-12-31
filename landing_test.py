
import os
import django
from django.test import RequestFactory
from django.urls import reverse

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from marketing.views import landing_page
from marketing.models import Feedback

# Test GET
factory = RequestFactory()
request = factory.get('/')
response = landing_page(request)
print(f"GET / Response Status: {response.status_code}")
if response.status_code == 200:
    print("GET / Success")
else:
    print("GET / Failed")

# Test POST (Feedback)
data = {
    'name': 'Test User',
    'phone': '1234567890',
    'email': 'test@example.com',
    'message': 'This is a test feedback message.'
}
request = factory.post('/', data)
response = landing_page(request)
print(f"POST / Response Status: {response.status_code}")

# Verify Database
last_feedback = Feedback.objects.last()
if last_feedback and last_feedback.email == 'test@example.com':
    print(f"Database Verification Success: Found feedback from {last_feedback.name}")
else:
    print("Database Verification Failed")
