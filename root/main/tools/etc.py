
__all__ = ('DJANGO_CONFIG', 'DATABASE_CONFIG', 'CLOUDINARY_CONFIG', 'GOOGLE_AUTH_CONFIG')

from pathlib import Path
import json

BASE_DIR = Path(__file__).parents[3]
CONFIG_DIR = BASE_DIR / 'etc'
CONFIG_DIR.mkdir(exist_ok=True)


DJANGO_FILE_CONFIG = CONFIG_DIR / 'config.json'
DATABASE_FILE_CONFIG = CONFIG_DIR / 'db_config.json'
CLOUDINARY_FILE_CONFIG = CONFIG_DIR / 'cloudinary_config.json'
GOOGLE_AUTH_FILE_CONFIG = CONFIG_DIR / 'google_config.json'

# Creations
if not DJANGO_FILE_CONFIG.exists():
    print(f"Configure your {CONFIG_DIR}")

    with DJANGO_FILE_CONFIG.open(mode='w') as js_file:
        json.dump({"DEBUG": "True",
                   "SECRET_KEY": "django-insecure-_____________________to_change____________________",
                   "EMAIL": "",
                   "EMAIL_PASSWORD": "",
                   "ALLOWED_HOSTS": ('127.0.0.1',)}, js_file)

    with DATABASE_FILE_CONFIG.open(mode='w') as js_file:
        json.dump({'default': {'ENGINE': 'django.db.backends.sqlite3',
                               'NAME': str(BASE_DIR / 'database.sqlite3'),
                               'TEST': {'NAME': ':memory:', "ENGINE": "django.db.backends.sqlite3"}}}, js_file)

    with CLOUDINARY_FILE_CONFIG.open(mode='w') as js_file:
        json.dump({'cloud_name': "",
                   'api_key': "",
                   'api_secret': ""}, js_file)

    with GOOGLE_AUTH_FILE_CONFIG.open(mode='w') as js_file:
        json.dump({"web": {"client_id": "",
                           "project_id": "",
                           "auth_uri": "",
                           "token_uri": "",
                           "auth_provider_x509_cert_url": "",
                           "client_secret": ""}}, js_file)


# Loadings
with DJANGO_FILE_CONFIG.open(mode='r') as js_file:
    DJANGO_CONFIG = json.load(js_file)

with DATABASE_FILE_CONFIG.open(mode='r') as js_file:
    DATABASE_CONFIG = json.load(js_file)

with CLOUDINARY_FILE_CONFIG.open(mode='r') as js_file:
    CLOUDINARY_CONFIG = json.load(js_file)

with GOOGLE_AUTH_FILE_CONFIG.open(mode='r') as js_file:
    GOOGLE_AUTH_CONFIG = json.load(js_file)

if __name__ == '__main__':
    print(DJANGO_CONFIG)
    print(DATABASE_CONFIG)
    print(CLOUDINARY_CONFIG)
    print(GOOGLE_AUTH_CONFIG)
