from django.conf.urls.defaults import *
from django.conf import settings

# Admin
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
	# Accounts
	(r'^user/search/$', 'movielistr.accounts.views.user_search'),
	(r'^stats/(?P<user_id>.*)/$', 'movielistr.accounts.views.img_stats'),
	(r'^friends/(?P<user_id>.*)/$', 'movielistr.accounts.views.toggle_friend'),
	(r'^user/(?P<user_id>.*)/$', 'movielistr.accounts.views.view_user'),
	(r'^account/$', 'movielistr.accounts.views.account'),
	(r'^login/$', 'movielistr.accounts.views.login_view'),
	(r'^doLogin/$', 'movielistr.accounts.views.do_login'),
	(r'^logout/$', 'movielistr.accounts.views.logout_view'),
	(r'^register/$', 'movielistr.accounts.views.register'),
	(r'^doRegister/$', 'movielistr.accounts.views.do_register'),
	(r'^recover/$', 'movielistr.accounts.views.recover'),
	(r'^doRecover/$', 'movielistr.accounts.views.do_recover'),
	(r'^post_recover/(?P<shash>.*)/$', 'movielistr.accounts.views.post_recover'),
	(r'^chngpwd/$', 'movielistr.accounts.views.chngpwd'),
	(r'^do_chngpwd/$', 'movielistr.accounts.views.do_chngpwd'),

	# Movies
	(r'^comment/del/(?P<comment_id>.*)/$', 'movielistr.movies.views.del_comment'),
	(r'^search_location/$', 'movielistr.movies.views.search_location'),
	(r'^movie/comment/(?P<movie_id>.*)/$', 'movielistr.movies.views.add_comment'),
	(r'^movie/(?P<movie_id>.*)/$', 'movielistr.movies.views.view_movie'),
	(r'^library/edit/(?P<movie_id>.*)/$', 'movielistr.movies.views.edit_library'),
	(r'^locations/del/(?P<loc_id>.*)/$', 'movielistr.movies.views.del_location'),
	(r'^locations/edit/(?P<loc_id>.*)/$', 'movielistr.movies.views.edit_location'),
	(r'^view_location/(?P<loc_id>.*)/$', 'movielistr.movies.views.view_location'),
	(r'^locations/(?P<user_id>.*)/$', 'movielistr.movies.views.locations'),
	(r'^wishlists/(?P<user_id>.*)/$', 'movielistr.movies.views.view_wishlist'),
	(r'^libraries/(?P<user_id>.*)/$', 'movielistr.movies.views.view_library'),
	(r'^ac_tags$', 'movielistr.movies.views.ac_tags'),
	(r'^library/remove_movie/(?P<movie_id>.*)/$', 'movielistr.movies.views.remove_movie'),
	(r'^library/remove_movie_wishlist/(?P<movie_id>.*)/$', 'movielistr.movies.views.remove_movie_wishlist'),
	(r'^library/add_movie_wishlist/(?P<movie_id>.*)/$', 'movielistr.movies.views.add_movie_wishlist'),
	(r'^library/add_movie/(?P<movie_id>.*)/$', 'movielistr.movies.views.add_movie'),
	(r'^movies/$', 'movielistr.movies.views.index'),
	(r'^find_related/$', 'movielistr.movies.views.find_related'),
	(r'^find_trailers/$', 'movielistr.movies.views.find_trailers'),
	(r'^netflix/$', 'movielistr.movies.views.netflix'),

	# Forums
	(r'^forums/(?P<cat_id>.*)/add_thread/$', 'movielistr.forums.views.add_thread'),
	(r'^forums/(?P<cat_id>.*)/(?P<thread_id>.*)/$', 'movielistr.forums.views.view_thread'),
	(r'^forums/(?P<cat_id>.*)/$', 'movielistr.forums.views.view_cat'),
	(r'^forums/$', 'movielistr.forums.views.index'),

	# Portada
	(r'^$', 'movielistr.movies.views.home'),

	# Static media
	(r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_DOC_ROOT}),

	# Admin static media
	(r'^admin_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.ADMIN_DOC_ROOT}),

    # Admin
    url(r'^admin/', include(admin.site.urls)),
)
