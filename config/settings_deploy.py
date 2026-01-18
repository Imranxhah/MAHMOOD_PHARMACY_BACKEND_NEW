import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv
import pillow_avif # Register AVIF plugin

# Load environment variables
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ==============================================
# 1. SECURITY SETTINGS
#Override these in your production .env file
# ==============================================

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-uj#ic6m_jirde8p%%9hmtx2byng2u#2xxk94g7p7!6s%&ur!jy')

# SECURITY WARNING: don't run with debug turned on in production!
# Default to False in production for safety
DEBUG = os.getenv('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = [
    'mpharmacy.pythonanywhere.com',
    'www.mpharmacy.pythonanywhere.com',
    'localhost',
    '127.0.0.1',
    '10.0.2.2',  # Android Emulator
]

# ==============================================
# 2. INSTALLED APPS & MIDDLEWARE
# ==============================================

INSTALLED_APPS = [
    'jazzmin',  # Must be before admin
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third Party Apps
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'django_cleanup.apps.CleanupConfig',  # Auto-deletes old files
    'import_export',                      # For Batch Uploads

    # My Apps
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


# ==============================================
# 3. DATABASE
# ==============================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# ==============================================
# 4. PASSWORD VALIDATION & AUTH
# ==============================================

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

AUTH_USER_MODEL = 'users.User'


# ==============================================
# 5. INTERNATIONALIZATION & TIMEZONE
# ==============================================

LANGUAGE_CODE = 'en-us'

# CRITICAL: Ensures reports show correct Pakistan Time
TIME_ZONE = 'Asia/Karachi'

USE_I18N = True
USE_TZ = True


# ==============================================
# 6. STATIC & MEDIA FILES
# ==============================================

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# ==============================================
# 7. EMAIL CONFIGURATION
# ==============================================

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = f"Mahmood Pharmacy <{os.getenv('EMAIL_HOST_USER')}>"


# ==============================================
# 8. API & SECURITY (DRF, JWT, CORS)
# ==============================================

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
        'rest_framework.throttling.ScopedRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',
        'user': '1000/day',
        'otp': '5/min',
    }
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=390),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=390),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}

OTP_EXPIRATION_MINUTES = 10

# CORS Settings
CORS_ALLOW_ALL_ORIGINS = True  # Recommend False in production and filling allowed origins below
CORS_ALLOWED_ORIGINS = [
    "https://mpharmacy.pythonanywhere.com",
    "http://localhost:3000",
    # Add your Flutter app request domain here if needed
]


# ==============================================
# 9. THIRD PARTY APP SETTINGS
# ==============================================

# Fix for Django 5.x Import-Export Crash
IMPORT_EXPORT_SKIP_ADMIN_LOG = True

# JAZZMIN Settings (Exact Copy)
JAZZMIN_SETTINGS = {
    "site_title": "Mahmood Pharmacy Admin",
    "site_header": "Mahmood Pharmacy",
    "site_brand": "Mahmood Pharmacy",
    "welcome_sign": "Welcome to the Mahmood Pharmacy Admin Panel",
    "copyright": "Mahmood Pharmacy Ltd",
    "show_sidebar": True,
    "navigation_expanded": False,
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "users.User": "fas fa-user",
    },
    "custom_css": "css/custom_admin.css",
    "custom_js": "js/custom_admin.js",
    "show_ui_builder": False, # Set to True to customize, False for Prod
    "changeform_format": "horizontal_tabs",
    "topmenu_links": [
        {"name": "Home",  "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "Dashboard", "url": "admin-charts", "permissions": ["auth.view_user"], "icon": "fas fa-chart-line"},
        {"name": "Generate Sales Report", "url": "sales_report"},
    ],
    "custom_links": {
        "orders": [
            {
                "name": "Analytics Dashboard",
                "url": "admin-charts",
                "icon": "fas fa-chart-line",
                "permissions": ["auth.view_user"]
            },
            {
                "name": "Sales Report",
                "url": "sales_report",
                "icon": "fas fa-file-invoice-dollar",
                "permissions": ["orders.view_order"]
            }
        ]
    },
}

JAZZMIN_UI_TWEAKS = {
    "theme": "lux",
    "navbar": "navbar-cyan navbar-dark",
    "accent": "accent-primary",
    "sidebar": "sidebar-dark-primary",
}
