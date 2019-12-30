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
        'NAME': 'textmap',
        'USER': 'textmap',
        'PASSWORD': 'sn3',
        'HOST': 'localhost',
        'PORT': 5432,
    }
}
