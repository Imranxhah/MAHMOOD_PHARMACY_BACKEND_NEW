import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv

# 1. Load environment variables
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# 2. SECURITY: Get secret key from .env
# Never hardcode this in production
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-default-key-change-this')

# 3. SECURITY: Turn off Debug in production
DEBUG = os.getenv('DEBUG', 'False') == 'True'

# 4. Allowed Hosts
ALLOWED_HOSTS = ['mahmoodpharmacy.pythonanywhere.com', '127.0.0.1', 'localhost']

# Application definition
INSTALLED_APPS = [
    'jazzmin', 
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'users',
    'products',
    'orders',
    'prescriptions',
    'branches',
    'analytics',
    'marketing',
    'notifications',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# 5. Email Configuration (Using .env variables)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = f"Mahmood Pharmacy <{os.getenv('EMAIL_HOST_USER')}>"

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# 6. Static and Media Files
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

AUTH_USER_MODEL = 'users.User'

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
        'rest_framework.throttling.ScopedRateThrottle', # Ensure this is present
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',
        'user': '1000/day',
        'otp': '5/min', # FIX: Added missing rate for 'otp' scope
    }
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=90),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}

OTP_EXPIRATION_MINUTES = 10

# 7. CORS Configuration
CORS_ALLOW_ALL_ORIGINS = False  # Set to False for production!
CORS_ALLOWED_ORIGINS = [
    "https://mahmoodpharmacy.pythonanywhere.com",
    # Add your frontend URL here (e.g. Flutter web or React app URL)
]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# JAZZMIN Settings (Kept exactly as you had them)
JAZZMIN_SETTINGS = {
    "site_title": "Mahmood Pharmacy Admin",
    "site_header": "Mahmood Pharmacy",
    "site_brand": "Mahmood Pharmacy",
    "welcome_sign": "Welcome to the Mahmood Pharmacy Admin Panel",
    "copyright": "Mahmood Pharmacy Ltd",
    "search_model": ["users.User"],
    "show_sidebar": True,
    "navigation_expanded": True,
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "users.User": "fas fa-user",
    },
    "custom_css": "css/custom_admin.css",
    "custom_js": "js/custom_admin.js",
    "show_ui_builder": False, # Turned off for production
    "changeform_format": "horizontal_tabs",
}

JAZZMIN_UI_TWEAKS = {
    "theme": "lux",
    "navbar": "navbar-cyan navbar-dark",
    "accent": "accent-primary",
    "sidebar": "sidebar-dark-primary",
}
