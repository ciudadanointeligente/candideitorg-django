SECRET_KEY = '...hahaha...'

INSTALLED_APPS = [
    'candideitorg',
    'djcelery'
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME":   "candideitorg-django.sqlite3",
    }
}
CANDIDEITORG_URL = 'http://127.0.0.1:3002/api/v2/'
CANDIDEITORG_USERNAME = 'admin'
CANDIDEITORG_API_KEY = 'a'

import djcelery
djcelery.setup_loader()

CELERY_ALWAYS_EAGER = True
