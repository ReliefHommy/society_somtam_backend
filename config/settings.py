
import os
import platform
from pathlib import Path
from dotenv import load_dotenv

# Make sure OSGeo4W DLLs are discoverable
os.environ["PATH"] = r"C:\Users\ratan\AppData\Local\Programs\OSGeo4W\bin;" + os.environ.get("PATH", "")

# GeoDjango (Windows)
# GeoDjango (Windows / OSGeo4W) — ONLY for local Windows dev
if platform.system() == "Windows":
    OSGEO4W_ROOT = r"C:\Users\ratan\AppData\Local\Programs\OSGeo4W"

    try:
        os.add_dll_directory(rf"{OSGEO4W_ROOT}\bin")
    except Exception:
        pass

    os.environ["PATH"] = rf"{OSGEO4W_ROOT}\bin;" + os.environ.get("PATH", "")

    GDAL_LIBRARY_PATH = rf"{OSGEO4W_ROOT}\bin\gdal312.dll"
    GEOS_LIBRARY_PATH = rf"{OSGEO4W_ROOT}\bin\geos_c.dll"
    os.environ["PROJ_LIB"] = rf"{OSGEO4W_ROOT}\share\proj"
    os.environ["GDAL_DATA"] = rf"{OSGEO4W_ROOT}\apps\gdal\share\gdal"



GDAL_LIBRARY_PATH = r"C:\Users\ratan\AppData\Local\Programs\OSGeo4W\bin\gdal312.dll"
GEOS_LIBRARY_PATH = r"C:\Users\ratan\AppData\Local\Programs\OSGeo4W\bin\geos_c.dll"

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "dev-only")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEBUG = ENVIRONMENT != "production"

#ALLOWED_HOSTS


ALLOWED_HOSTS = [h.strip() for h in os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",") if h.strip()]
CORS_ALLOWED_ORIGINS = [o.strip() for o in os.getenv("CORS_ALLOWED_ORIGINS", "").split(",") if o.strip()]



# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    "corsheaders",
    "ninja",
    "society",
    "accounts",
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
]



ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

import dj_database_url

DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv("DATABASE_URL"),
        conn_max_age=600,
    )
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
