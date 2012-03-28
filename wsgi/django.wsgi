import os
import sys

sys.path.append('/var/www')
sys.path.append('/var/www/movielistr/')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "movielistr.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
