#  Copyright (c) 2019 Brian Schubert
#
#  This file is distributed under the MIT License. If a copy of the
#  MIT License was not distributed with this file, you can obtain one
#  at https://opensource.org/licenses/MIT.

SECRET_KEY = 'supr-s3krit-kee'

INSTALLED_APPS = [
    'django.contrib.sessions',
    "django_htcpcp_tea",
]

MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django_htcpcp_tea.middleware.HTCPCPTeaMiddleware',
]

# Use in-memory SQLite database for tests
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
    },
]
