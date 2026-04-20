import os
import logging
from datetime import timedelta
from pathlib import Path
from corsheaders.defaults import default_headers

logging.basicConfig(
    level=logging.ERROR,
    format='\n\n%(asctime)s %(levelname)s %(message)s',
    handlers=[
        logging.StreamHandler(),            # вывод в консоль
        logging.FileHandler('errors.log'),  # и в файл errors.log
    ]
)

UNCONFIRMED_USER_EXPIRATION_HOURS = 24

EXAM_MARKS_PERCENT = {2: 50, 3: 70, 4: 85, 5: 100}

BASE_DIR = Path(__file__).resolve().parent.parent

AUTH_USER_MODEL = 'api.User'

SECRET_KEY = 'django-insecure-)5n(o&ufyhjps8px)2v1td*!7(mz4ex%t98ekxm8vt0z7_&6qc'

DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_apscheduler',
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'api.apps.ApiConfig',
    'drf_yasg',
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

# Подключение PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'edu-db',
        'USER': 'admin',
        'PASSWORD': 'admin',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Настройки аутентификации (JWT)
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'api.authentication.CookieJWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    )
}

SWAGGER_SETTINGS = {
    'USE_SESSION_AUTH': False,
    'SECURITY_DEFINITIONS': {
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header',
            'description': 'Вставьте токен вида: Bearer <access_token>'
        }
    }
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),  # Срок действия Access токена
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),  # Срок действия Refresh токена
    'ROTATE_REFRESH_TOKENS': True,  # Используется для обновления refresh токенов
    'BLACKLIST_AFTER_ROTATION': True,  # Блокировать старые refresh токены после обновления
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}

# CORS настройки (если фронт будет на другом домене)
# CORS_ALLOWED_ORIGINS = [
#     'http://localhost:3000',  # React или другой фронтенд
# ]
CORS_ALLOW_CREDENTIALS = True  # Разрешить отправку авторизационных данных (cookies, JWT)
CORS_ALLOW_HEADERS = ['*']  # Разрешить все заголовки
CORS_ALLOW_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

CORS_ALLOW_HEADERS = list(default_headers) + [
    'content-type',
]
CORS_ALLOW_ALL_ORIGINS = True

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'stellacorevanilla@gmail.com'
EMAIL_HOST_PASSWORD = 'ckqovtpieokgczaa'

# MEDIA файлы
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Статические файлы (CSS, JavaScript, изображения)
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')


ROOT_URLCONF = 'educert_backend.urls'

# Папка для импорта файлов
IMPORTS_DIR = os.path.join(MEDIA_ROOT, 'imports')
IMPORT_USERS_DIR = os.path.join(IMPORTS_DIR, 'users')
IMPORT_TESTS_DIR = os.path.join(IMPORTS_DIR, 'tests')
os.makedirs(IMPORT_USERS_DIR, exist_ok=True)
os.makedirs(IMPORT_TESTS_DIR, exist_ok=True)