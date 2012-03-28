from django.contrib import admin
from movielistr.forums.models import *

admin.site.register(Category)
admin.site.register(Thread)
admin.site.register(Message)