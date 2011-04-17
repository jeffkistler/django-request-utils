import os

PROJECT_DIR = os.path.dirname(__file__)

DEBUG = True
TEMPLATE_DEBUG = DEBUG
SITE_ID = 1
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(PROJECT_DIR, 'test.db')
    }
}
TEMPLATE_DIRS = (os.path.join(PROJECT_DIR, 'templates'),)
INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.auth',
    'django.contrib.sites',
    'django.contrib.admin',
    'request_utils',
]
ROOT_URLCONF = 'testproject.urls'
MEDIA_URL = '/media/'
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
)
TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
