import os
from pathlib import Path

# ========================
# Add on top for Heroku
# ========================
import dj_database_url
from decouple import config

# ========================
# BASE_DIR
# ========================
BASE_DIR = Path(__file__).resolve().parent.parent

# ========================
# SECRET KEY & DEBUG
# ========================
SECRET_KEY = config('SECRET_KEY', default='unsafe-secret-key')
DEBUG = config('DEBUG', default=True, cast=bool)

# ========================
# Allowed Hosts
# ========================
ALLOWED_HOSTS = ['*']

# ========================
# Installed Apps
# ========================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',        # आपका app
    'accounts',    # अगर accounts app है
]

# ========================
# Middleware
# ========================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Heroku static files
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# ========================
# URLS & WSGI
# ========================
ROOT_URLCONF = 'redvibe.urls'
WSGI_APPLICATION = 'redvibe.wsgi.application'

# ========================
# Database (Heroku ready)
# ========================
DATABASES = {
    'default': dj_database_url.config(default=f'sqlite:///{BASE_DIR}/db.sqlite3')
}

# ========================
# Password validators
# ========================
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# ========================
# Internationalization
# ========================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ========================
# Static files
# ========================
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ========================
# Default primary key field type
# ========================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

