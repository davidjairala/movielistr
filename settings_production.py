# Django settings for Flirkin project.

DEBUG = True # False or True
TEMPLATE_DEBUG = DEBUG # False or DEBUG

ADMINS = (
    ('David Jairala', 'davidjairala@gmail.com'),
)

#TOTAL_ROOT = '/Users/davidjairala/Dropbox/Projects/movielistr'
TOTAL_ROOT = '/var/www/movielistr'

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'movielistr',
        'USER': 'movielistr',
        'PASSWORD': 'g3hcm68s',
        'HOST': '',
        'PORT': '',
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/New_York'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = TOTAL_ROOT + '/media'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/admin_media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '0y@xec67x()w04v7r@#bts*sy^gf&gv$4w&cuxpwm$--fj-krd'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

ROOT_URLCONF = 'movielistr.urls'

TEMPLATE_DIRS = (
    TOTAL_ROOT + '/templates'
)

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    # Markup markdown
    'django.contrib.markup',
    # Para el admin
    'django.contrib.admin',
    # App
    'movielistr.movies',
    'movielistr.forums',
    'movielistr.accounts',
)

# Para media estatica
STATIC_DOC_ROOT = TOTAL_ROOT + '/media'
# Para media estatica del admin
ADMIN_DOC_ROOT = TOTAL_ROOT + '/admin_media'

# Para enviar mails
EMAIL_HOST = 'localhost'
EMAIL_PORT = '25'

# Para static files del admin
ADMIN_FILES_ROOT = '/var/django/media'

# Para uploads
UPLOAD_FILES = TOTAL_ROOT + '/media/uploads/'

# Cache
CACHE_ROOT = STATIC_DOC_ROOT + '/cache'
CACHETIME = 60 * 15
# Produccion
CACHE_BACKEND = 'file://' + CACHE_ROOT
# Pruebas
#CACHE_BACKEND = 'dummy:///'

# De la app