from django.contrib import admin
from movielistr.movies.models import *

admin.site.register(Movie)
admin.site.register(MovieDirectory)
admin.site.register(MovieUser)
admin.site.register(Comment)
admin.site.register(Location)
admin.site.register(Trailer)
admin.site.register(TrailerLastSearched)
admin.site.register(Related)
admin.site.register(LastRelated)