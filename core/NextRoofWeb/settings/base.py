DEBUG = False
SECRET_KEY = NotImplemented
from ...main.session import session_middleware
from .dev import db

CSRF_TRUSTED_ORIGINS = ['https://www.nextroof.co.il']

ALLOWED_HOSTS = [
    'nextroof.online', 'www.nextroof.online', '*', 'nextroof.online',
    'www.nextroof.co.il'
]
# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core.main.apps.MainConfig',
    'django_extensions',
]
# Remove-Item C:\Users\yoavl\NextRoofWeb\core\main\migrations\* -Force -Recurse
# New-Item -Path C:\Users\yoavl\NextRoofWeb\core\main\migrations\__init__.py -ItemType File

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.main.session.session_middleware',
]

ROOT_URLCONF = 'core.NextRoofWeb.urls'

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
                'core.NextRoofWeb.settings.templates.user_context_processor.user_info',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.NextRoofWeb.wsgi.application'

DATABASES = db

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME':
        'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME':
        'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME':
        'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME':
        'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# poetry run python -m core.manage collectstatic
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'static'  # type: ignore # noqa: F821
STATICFILES_DIRS = [BASE_DIR / 'core' / 'static']  # type: ignore # noqa: F821

MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')  # type: ignore # noqa: F821
MEDIA_URL = '/media/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
