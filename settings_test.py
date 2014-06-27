
# encoding=UTF-8
# Django settings for candidator project.
import os

INSTALLED_APPS = [
    'candideitorg',
    'djcelery'
]

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': os.path.join(PROJECT_ROOT, 'development.db'),                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}
import djcelery
djcelery.setup_loader()

CELERY_ALWAYS_EAGER = True

#CELERY STUFF
BROKER_URL = 'amqp://guest:guest@localhost:5672/'
CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'
CELERY_RESULT_BACKEND = "amqp"
SECRET_KEY="hola"
CANDIDEITORG_URL = 'http://127.0.0.1:3002/api/v2/'
CANDIDEITORG_USERNAME = 'admin'
CANDIDEITORG_API_KEY = 'a'

import djcelery
djcelery.setup_loader()

CELERY_ALWAYS_EAGER = True
