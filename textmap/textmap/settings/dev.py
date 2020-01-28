import os

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '4(#8jc9j03jv5mrp)$1_oame0!#ii)(-+pm+szw9@!49%mez+y'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.getenv('POSTGRES_DB', 'textmap'),
        'USER': os.getenv('POSTGRES_USER', 'textmap'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'sn3'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', 5432),
    }
}

MEDIA_ROOT = os.getenv('MEDIA_ROOT', '/var/www/textmap/media/')
MEDIA_URL = ''
