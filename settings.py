SECRET_KEY = '...hahaha...'

INSTALLED_APPS = [
    'candideitorg',
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME":   "candideitorg-django.sqlite3",
    }
}