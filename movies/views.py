from django.http import HttpResponseRedirect
from django.views.generic.simple import direct_to_template
from django.db.models import Q
from movielistr.movies.models import *
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.core.mail import mail_admins

# =========================================================
# Helpers
# =========================================================

# Helper for netflix
def doSearch(netflix, discs, arg):
	data = netflix.catalog.searchTitles(arg,0,30)
	return data

# Helper netflix similar
def doSearchSimilars(netflix, discs, arg):
	data = netflix.catalog.searchSimilars(arg,0,20)
	return data

# Helper - makes html string for movies
def htmlizeMovies(request, movies):
	r_movies_html = ''
	if(movies):
		for movie in movies:
			try:
				title = movie.title
			except:
				movie = movie.movie
			has_movie = movie.hasMovie(request.user)
			has_wishlist = movie.hasWishlist(request.user)
			if(has_wishlist):
				wl_link = '<a href="#" title="Remove from your wish list" onclick="removeMovieFromWishlist(' + str(movie.id) + '); return false;"><img id="movie_img_favorite_' + str(movie.id) + '" src="/site_media/imgs/favorite_16.png" alt="" class="vmiddle" /></a> '
			else:
				wl_link = '<a href="#" title="Add to your wish list" onclick="addMovieToWishlist(' + str(movie.id) + '); return false;"><img id="movie_img_favorite_' + str(movie.id) + '" src="/site_media/imgs/favorite_off_16.png" alt="" class="vmiddle" /></a> '
			if(has_movie):
				mclass = 'movie_box_already_added'
			else:
				mclass = 'movie_box'
			if not request.user.is_authenticated() or not has_movie:
				add_btns = '<a href="#" title="Add this movie to your library" onclick="addMovieToLibrary(' + str(movie.id) + '); return false;"><img src="/site_media/imgs/add_16.png" alt="" class="vmiddle" /></a>\
				<a href="#" title="Add this movie to your library" onclick="addMovieToLibrary(' + str(movie.id) + '); return false;">Add</a> '
			else:
				add_btns = '<a href="#" title="Remove this movie from your library" onclick="removeMovieFromLibrary(' + str(movie.id) + '); return false;"><img src="/site_media/imgs/del_16.png" alt="" class="vmiddle" /></a>\
				<a href="#" title="Remove this movie from your library" onclick="removeMovieFromLibrary(' + str(movie.id) + '); return false;">Remove</a> | \
				<a href="/library/edit/' + str(movie.id) + '/">Edit</a> '
				wl_link = ''
			if(request.user.is_staff):
				admin_btns = ' [ <a href="/admin/movies/movie/' + str(movie.id) + '/">e</a> ]'
			else:
				admin_btns = ''
			r_movies_html += '<div class="' + mclass + '" id="boxxed_movie_' + str(movie.id) + '">\
				<div class="add">\
					' + add_btns + wl_link + admin_btns + '\
				</div>\
				<div class="box_art">\
					<a href="/movie/' + str(movie.id) + '/" title="' + movie.title + '"><img src="' + movie.box_art_big + '" alt="" style="width:110px; height:151px;" /></a>\
				</div>\
				<div class="title">\
					<a href="/movie/'+ str(movie.id)+ '/" title="' + movie.title + '">' + movie.short_title() + '</a>\
				</div>\
			</div>'
	return r_movies_html

# =========================================================
# /Helpers
# =========================================================

# Deletes a comment
def del_comment(request, comment_id):
	if(request.user.is_staff):
		try:
			comment = Comment.objects.get(pk=comment_id)
			movie_id = comment.movie.id
			comment.delete()
			return HttpResponseRedirect('/movie/' + str(movie_id) + '/?info=deleted_comment')
		except:
			return direct_to_template(request, 'err_404.html', {  })
	else:
		return direct_to_template(request, 'err_perms.html', {  })

# Adds a comment to a movie
def add_comment(request, movie_id):
	if(request.POST['comment']):
		if(request.user.is_authenticated()):
			try:
				movie = Movie.objects.get(pk=movie_id)
				comment = request.POST['comment']
				if(comment != ''):
					# Check if we must use cheat user
					try:
						user = User.objects.get(pk=request.POST['cheat_user'])
					except:
						user = request.user
					new_comment = Comment(movie = movie, user = user, comment = comment)
					new_comment.save()
					mail_admins('MovieListr - New comment', 'New comment in MovieListr:\n\nhttp://movielistr.com/movie/' + str(movie.id) + '\n\nUser:\n' + user.username + '\n\nComment:\n' + comment, fail_silently=True)
					return HttpResponseRedirect('/movie/' + movie_id + '/?info=added_comment')
				else:
					return HttpResponseRedirect('/movie/' + movie_id + '/?error=no_comment')
			except:
				return direct_to_template(request, 'err_404.html', {  })
		else:
			return direct_to_template(request, 'login_req.html', { 'next':'/movie/' + movie_id + '/' })
	else:
		return HttpResponseRedirect('/movie/' + movie_id + '/')

# Search a location
def search_location(request):
	try:
		loc = request.GET['loc']
		try:
			location = Location.objects.filter(user = request.user, tag=loc)[0]
			return HttpResponseRedirect('/view_location/' + str(location.id) + '/')
		except:
			pass
	except:
		pass
	return direct_to_template(request, 'err_404.html', {  })

# View a movie
def view_movie(request, movie_id):
	staff_users = None
	try:
		movie = Movie.objects.get(pk=movie_id)
		has_movie = movie.hasMovie(request.user)
		has_wishlist = movie.hasWishlist(request.user)
		trailer = movie.has_trailer()
		if(request.user.is_staff):
			staff_users = User.objects.filter(is_staff=True).order_by('username')
		try:
			mu = MovieUser.objects.filter(movie = movie, user = request.user)[0]
		except:
			mu = None
		try:
			error = request.GET['error']
		except:
			error = None
		try:
			info = request.GET['info']
		except:
			info = None
		pagesize = 20
		try:
			pnum = int(request.GET['page'])
		except:
			pnum = 1
		comments = Comment.objects.filter(movie = movie).order_by('added')
		p = Paginator(comments, pagesize)
		p = p.page(pnum)
		# Similar movies
		rels_html = ''
		try:
			rels = Related.objects.filter(movie = movie).order_by('related__title')[:24]
			movies = []
			for rel in rels:
				movies.append(rel.related)
			if rels:
				rels_html = htmlizeMovies(request, movies)
		except:
			rels = None
		return direct_to_template(request, 'movies/view_movie.html', { 'movie':movie, 'has_movie':has_movie, 'has_wishlist':has_wishlist, 'mu':mu, 'trailer':trailer, 'staff_users':staff_users, 'error':error, 'info':info, 'comments':p, 'rels':rels, 'rels_html':rels_html })
	except:
		return direct_to_template(request, 'err_404.html', {  })

# Edits a movie in the users library
def edit_library(request, movie_id):
	err = None
	if(request.user.is_authenticated()):
		try:
			movie = Movie.objects.get(pk=movie_id)
			try:
				mu = MovieUser.objects.filter(user = request.user, movie = movie)[0]
				if(request.POST):
					location = request.POST['location']
					notes = request.POST['notes']
					if(location != ''):
						mu.location = location
						mu.notes = notes
						mu.save()
						tags = location.split(',')
						tags_arr = []
						for tag in tags:
							tag = tag.strip()
							if(tag != ''):
								tags_arr.append(tag)
								try:
									alr_location = Location.objects.filter(user = request.user, tag = tag)[0]
								except:
									# Doesnt exist, go on
									new_location = Location(user = request.user, tag = tag)
									new_location.save()
						return HttpResponseRedirect('/libraries/' + str(request.user.id) + '/?info=modded')
					else:
						err = "Please fill in the location where you have stored the movie."
				return direct_to_template(request, 'movies/edit_library.html', { 'movie':movie, 'mu':mu, 'err':err, 'movie':movie })
			except:
				return direct_to_template(request, 'err_404.html', {  })
		except:
			return direct_to_template(request, 'err_404.html', {  })
	else:
		return direct_to_template(request, 'login_req.html', { 'next':'/library/edit/' + movie_id + '/' })

# Delete a location
def del_location(request, loc_id):
	import re
	if(request.user.is_authenticated()):
		try:
			location = Location.objects.get(pk=loc_id)
			if(location.user.id == request.user.id):
				err = None
				tag = ''
				old_tag = location.tag
				mus = MovieUser.objects.filter(user = request.user)
				for mu in mus:
					tags = mu.location
					tags_arr = tags.split(',')
					final_tags_arr = []
					for t in tags_arr:
						t = t.strip()
						if(t != '' and t != old_tag):
							final_tags_arr.append(t)
					mu.location = ','.join(final_tags_arr)
					mu.save()
				location.delete()
				return HttpResponseRedirect('/locations/' + str(request.user.id) + '/?info=removed')
			else:
				return direct_to_template(request, 'err_perms.html', {  })
		except:
			return direct_to_template(request, 'err_404.html', {  })
	else:
		return direct_to_template(request, 'login_req.html', { 'next':'/locations/edit/' + loc_id + '/' })

# Edit a location
def edit_location(request, loc_id):
	import re
	if(request.user.is_authenticated()):
		try:
			location = Location.objects.get(pk=loc_id)
			if(location.user.id == request.user.id):
				err = None
				if(request.POST):
					tag = request.POST['tag']
					if(tag != ''):
						old_tag = location.tag
						mus = MovieUser.objects.filter(user = request.user)
						for mu in mus:
							mu.location = re.sub(old_tag, tag, mu.location)
							mu.save()
						location.tag = tag
						location.save()
						return HttpResponseRedirect('/locations/' + str(request.user.id) + '/?info=modded')
					else:
						err = "You can't leave the location field blank."
				return direct_to_template(request, 'movies/edit_location.html', { 'location':location, 'err':err })
			else:
				return direct_to_template(request, 'err_perms.html', {  })
		except:
			return direct_to_template(request, 'err_404.html', {  })
	else:
		return direct_to_template(request, 'login_req.html', { 'next':'/locations/edit/' + loc_id + '/' })

# Views a location
def view_location(request, loc_id):
	err = None
	location = None
	try:
		location = Location.objects.get(pk=loc_id)
		pagesize = 24
		try:
			pnum = int(request.GET['page'])
		except:
			pnum = 1
		movies = MovieUser.objects.filter(user = location.user, location__icontains=location.tag).order_by('movie__title')
		p = Paginator(movies, pagesize)
		p = p.page(pnum)
		movies_html = htmlizeMovies(request, p.object_list)
	except:
		err = "We couldn't find the location you're looking for, please try again."
	return direct_to_template(request, 'movies/view_location.html', { 'err':err, 'location':location, 'movies':p, 'movies_html':movies_html, 'pnum':pnum })

# View user's locations
def locations(request, user_id):
	err = None
	loc_user = None
	locations = None
	try:
		info = request.GET['info']
	except:
		info = None
	try:
		loc_user = User.objects.get(pk=user_id)
		locations = Location.objects.filter(user=loc_user).order_by('tag')
	except:
		err = "We couldn't find the user you're looking for."
	return direct_to_template(request, 'movies/locations.html', { 'err':err, 'loc_user':loc_user, 'locations':locations, 'info':info })

# View user wishlist
def view_wishlist(request, user_id):
	import re
	exact = None
	try:
		info = request.GET['info']
	except:
		info = None
	pagesize = 24
	try:
		pnum = int(request.GET['page'])
	except:
		pnum = 1
	try:
		sort = request.GET['sort']
	except:
		sort = 'title'
	if(sort == 'high_scores'):
		qsort = '-movie__score'
	elif(sort == 'most_added'):
		qsort = '-movie__owned_by'
	elif(sort == 'added_on'):
		qsort = '-movie__id'
	else:
		qsort = 'movie__title'
	movies_html = ''
	movies = False
	q = None
	slink = None
	p = None
	wl_user = None
	try:
		wl_user = User.objects.get(pk=user_id)
		try:
			try:
				q = request.GET['q']
				qs = q.strip()
				if(qs != ''):
					p = re.compile('\s+')
					qs = p.sub('(.*)', qs)
					try:
						exact = request.GET['exact']
						qs = '^' + qs + '$'
					except:
						pass
					movies = Wishlist.objects.filter(Q(user=wl_user) & (Q(movie__title__iregex=qs) | Q(movie__rating__iregex=qs) | Q(movie__genres__iregex=qs))).order_by(qsort)
					slink = '&q=%s' % (q)
				else:
					movies = None
			except:
				movies = None

			if(not movies):
				movies = Wishlist.objects.filter(user=wl_user).order_by(qsort)

			p = Paginator(movies, pagesize)
			p = p.page(pnum)

			movies_html = htmlizeMovies(request, p.object_list)
		except:
			err = "We couldn't find any movies for %s" % wl_user.username
		err = None
	except:
		err = "We couldn't find the library you were looking for."
	return direct_to_template(request, 'movies/view_wishlist.html', {'movies':p, 'movies_html':movies_html, 'err':err, 'wl_user':wl_user, 'q':q, 'slink':slink, 'info':info, 'pnum':pnum, 'sort':sort, 'exact':exact })

# View user library
def view_library(request, user_id):
	import re

	exact = None

	try:
		info = request.GET['info']
	except:
		info = None
	pagesize = 24
	try:
		pnum = int(request.GET['page'])
	except:
		pnum = 1
	try:
		sort = request.GET['sort']
	except:
		sort = 'title'
	if(sort == 'high_scores'):
		qsort = '-movie__score'
	elif(sort == 'most_added'):
		qsort = '-movie__owned_by'
	elif(sort == 'added_on'):
		qsort = '-movie__id'
	else:
		qsort = 'movie__title'
	movies_html = ''
	movies = False
	q = None
	slink = None
	p = None
	lib_user = None
	try:
		lib_user = User.objects.get(pk=user_id)
		try:
			try:
				q = request.GET['q']
				qs = q.strip()
				if(qs != ''):
					p = re.compile('\s+')
					qs = p.sub('(.*)', qs)
					try:
						exact = request.GET['exact']
						qs = '^' + qs + '$'
					except:
						pass
					movies = MovieUser.objects.filter(Q(user=lib_user) & (Q(movie__title__iregex=qs) | Q(movie__rating__iregex=qs) | Q(movie__genres__iregex=qs))).order_by(qsort)
					slink = '&q=%s' % (q)
				else:
					movies = None
			except:
				movies = None

			if(not movies):
				movies = MovieUser.objects.filter(user=lib_user).order_by(qsort)

			p = Paginator(movies, pagesize)
			p = p.page(pnum)

			movies_html = htmlizeMovies(request, p.object_list)
		except:
			err = "We couldn't find any movies for %s" % lib_user.username
		err = None
	except:
		err = "We couldn't find the library you were looking for."
	return direct_to_template(request, 'movies/view_library.html', {'movies':p, 'movies_html':movies_html, 'err':err, 'lib_user':lib_user, 'q':q, 'slink':slink, 'info':info, 'sort':sort, 'pnum':pnum, 'exact':exact })

# Autocomplete for tags
def ac_tags(request):
	if(request.user.is_authenticated()):
		q = request.GET['q']
		q = q.split(',')
		q = q[len(q) - 1].strip()
		tags = Location.objects.filter(user = request.user, tag__icontains=q)
		return direct_to_template(request, 'movies/ac_tags.html', {'tags':tags})
	else:
		return direct_to_template(request, 'ajax.html', {'out':''})

# Removes movie from library
def remove_movie(request, movie_id):
	try:
		movie = Movie.objects.get(pk=movie_id)
		if(request.user.is_authenticated()):
			# Check if it already exists in library
			try:
				mu = MovieUser.objects.filter(movie = movie, user = request.user)[0]
				# Exists, delete
				mu.delete()
				return direct_to_template(request, 'ajax.html', {'out':'ok'})
			except:
				pass
		else:
			return direct_to_template(request, 'ajax.html', {'out':'err_login'})
	except:
		return direct_to_template(request, 'ajax.html', {'out':'no_movie'})

# Remove movie from wishlist
def remove_movie_wishlist(request, movie_id):
	try:
		movie = Movie.objects.get(pk=movie_id)
		if(request.user.is_authenticated()):
			try:
				alr_wl = Wishlist.objects.filter(movie = movie, user = request.user)[0]
				# Exists, remove
				alr_wl.delete()
				return direct_to_template(request, 'ajax.html', {'out':'ok'})
			except:
				# Doesnt exist, error
				return direct_to_template(request, 'ajax.html', {'out':'alr'})
		else:
			return direct_to_template(request, 'ajax.html', {'out':'err_login'})
	except:
		return direct_to_template(request, 'ajax.html', {'out':'no_movie'})

# Add movie to wishlist
def add_movie_wishlist(request, movie_id):
	try:
		movie = Movie.objects.get(pk=movie_id)
		if(request.user.is_authenticated()):
			try:
				alr_wl = Wishlist.objects.filter(movie = movie, user = request.user)[0]
				# Exists, error
				return direct_to_template(request, 'ajax.html', {'out':'alr'})
			except:
				# Doesnt exist, add
				new_wl = Wishlist(movie = movie, user = request.user)
				new_wl.save()
				return direct_to_template(request, 'ajax.html', {'out':'ok'})
		else:
			return direct_to_template(request, 'ajax.html', {'out':'err_login'})
	except:
		return direct_to_template(request, 'ajax.html', {'out':'no_movie'})

# Shows form to add movie to library
def add_movie(request, movie_id):
	try:
		movie = Movie.objects.get(pk=movie_id)
		if(request.user.is_authenticated()):
			# Check if it already exists in library
			try:
				mu = MovieUser.objects.filter(movie = movie, user = request.user)[0]
				# Exists, error
				return direct_to_template(request, 'ajax.html', {'out':'alr'})
			except:
				# Doesnt exist already, go on
				if(request.POST):
					tags = request.POST['tags']
					tags = tags.split(',')
					tags_arr = []
					for tag in tags:
						tag = tag.strip()
						if(tag != ''):
							tags_arr.append(tag)
							try:
								alr_location = Location.objects.filter(user = request.user, tag = tag)[0]
							except:
								# Doesnt exist, go on
								new_location = Location(user = request.user, tag = tag)
								new_location.save()
					add_tags = ','.join(tags_arr)
					new_mu = MovieUser(movie = movie, user = request.user, location = add_tags)
					new_mu.save()
					# Add owned count
					try:
						movie.owned_by = movie.owned_by + 1
					except:
						movie.owned_by = 1
					# Remove from wishlist if it exists
					try:
						alr_wl = Wishlist.objects.filter(movie = movie, user = request.user)[0]
						# Exists, remove
						alr_wl.delete()
					except:
						# Doesnt exist, nothing
						pass
					return direct_to_template(request, 'ajax.html', {'out':'ok'})
				else:
					return direct_to_template(request, 'movies/add_movie.html', {'movie':movie})
		else:
			return direct_to_template(request, 'ajax.html', {'out':'err_login'})
	except:
		return direct_to_template(request, 'ajax.html', {'out':'no_movie'})

# Index
def index(request):
	import re

	exact = None

	pagesize = 24
	try:
		pnum = int(request.GET['page'])
	except:
		pnum = 1
	try:
		sort = request.GET['sort']
	except:
		sort = 'added_on'
	if(sort == 'high_scores'):
		qsort = '-score'
	elif(sort == 'most_added'):
		qsort = '-owned_by'
	elif(sort == 'added_on'):
		qsort = '-id'
	else:
		qsort = 'title'
	try:
		q = request.GET['q']
		qs = q.strip()
		if(qs != ''):
			p = re.compile('\s+')
			qs = p.sub('(.*)', qs)
			try:
				exact = request.GET['exact']
				qs = '^' + qs + '$'
			except:
				pass
			movies = Movie.objects.filter(Q(title__iregex=qs) | Q(rating__iregex=qs) | Q(genres__iregex=qs)).order_by(qsort)
			slink = '&q=%s' % (q)
		else:
			movies = None
	except:
		movies = None
	if(not movies):
		movies = Movie.objects.all().order_by(qsort)
		q = None
		slink = None

	p = Paginator(movies, pagesize)
	p = p.page(pnum)

	movie_html = ''

	if p.object_list:
		movie_html = htmlizeMovies(request, p.object_list)
	return direct_to_template(request, 'movies/index.html', {'btn':'movies', 'movies':p, 'slink':slink, 'q':q, 'movie_html':movie_html, 'pnum':pnum, 'sort':sort, 'exact':exact })

# Frontpage
def home(request):
	from movielistr.forums.models import *
	movie_html = ''
	movies = Movie.objects.all().order_by('-id')[:12]
	movie_html = htmlizeMovies(request, movies)
	threads = Thread.objects.all().order_by('-id')[:5]
	comments = Comment.objects.all().order_by('-id')[:5]
	return direct_to_template(request, 'movies/home.html', {'btn':'home', 'movie_html':movie_html,'threads':threads, 'comments':comments})

# Find trailers with youtube api
def find_trailers(request):
	import urllib2
	from BeautifulSoup import BeautifulSoup
	import re
	try:
		tls = TrailerLastSearched.objects.all().order_by('-id')[0]
		last_id = tls.movie.id
	except:
		# No last searched
		last_id = 0
	try:
		movie = Movie.objects.filter(id__gt=last_id)[0]

		key = 'AI39si75puGo2q7ZAMUcajIbCqYWpDxtfpFXQSmu1il7yXn3_mxFoY1bUcIe7fm9TjI8fG86pRoN7Brc3ofhLsw4e9THkgRbCw'
		url = 'http://gdata.youtube.com/feeds/api/videos?q=%(url)s&client=%(key)s' % { 'url':urllib2.quote(movie.title[0:25]), 'key':key }

		fh = urllib2.urlopen(url)
		html = fh.read()
		fh.close()

		soup = BeautifulSoup(html)

		links = soup.findAll('link')
		found = 'Nothing found: ' + movie.title
		for l in links:
			if(re.search('youtube_gdata', l['href'])):
				found = l['href']
				# Delete any previos trailers for the movie
				old_trailers = Trailer.objects.filter(movie = movie)
				for ot in old_trailers:
					ot.delete()
				new_trailer = Trailer(movie = movie, link = found)
				new_trailer.save()
				found = movie.title + ' : ' + found
				break

		# Save last searched
		tls = TrailerLastSearched.objects.all()
		for t in tls:
			t.delete()
		new_tls = TrailerLastSearched(movie = movie)
		new_tls.save()

		out = found
	except:
		# Done, no more movies
		try:
			out = movie.title
		except:
			out = ''
		out = 'Done - no more movies to do for now: ' + out
	return direct_to_template(request, 'ajax.html', {'out':out})

# Finds related movies
def find_related(request):
	from Netflix import *
	import getopt
	import time
	import simplejson
	import re
	import urllib2
	from BeautifulSoup import BeautifulSoup

	APP_NAME   = 'MovieListr'
	API_KEY    = 'netflix_api_key'
	API_SECRET = 'netflix_api_secret'
	CALLBACK   = ''
	verbose = False

	try:
		lr = LastRelated.objects.all().order_by('-id')[0]
		movie = Movie.objects.filter(id__gt=lr.movie.id)[0]
		lr.movie = movie
	except:
		# No last searched, grab first movie
		movie = Movie.objects.all().order_by('id')[0]
		lr = LastRelated(movie = movie)

	link = movie.link
	link_arr = link.split('/')
	try:
		movie_id = link_arr[6]
	except:
		movie_id = link_arr[4]
	netflixClient = NetflixClient(APP_NAME, API_KEY, API_SECRET, CALLBACK, verbose)
	discs=[]
	data = doSearchSimilars(netflixClient,discs,movie_id)

	out = ''

	for part in data['similars']['similars_item']:
		try:
			# Check if movie already exists
			link = part['id']
			link_parts = link.split('/')
			link_parts = link_parts[len(link_parts) - 1]
			link = 'http://www.netflix.com/Movie/' + link_parts
			try:
				alr_movie = Movie.objects.filter(link__contains=link_parts)[0]
				# Similar exists, go ahead
				# Check if similar doesnt exist already
				try:
					alr_related = Related.objects.filter(movie = movie, related = alr_movie)[0]
					# Exists, do nothing
				except:
					# Doesnt exist, add
					new_related = Related(movie = movie, related = alr_movie)
					new_related.save()
					out += 'Saved: ' + movie.title + ' -> ' + new_related.related.title + ' --- \n'
			except:
				# Doesnt exist, skip
				out += 'Skipped: ' + movie.title + ' -> ' + link + ' : Related does not exist --- \n'
		except:
			# Something went wrong, dont save movie
			out += 'Error in actual saving: ' + part['id'] + '\n'
	lr.save()
	return direct_to_template(request, 'ajax.html', {'out':out})

# Netflix api for a single title
def netflix(request):
	from Netflix import *
	import getopt
	import time
	import simplejson
	import re
	import urllib2
	from BeautifulSoup import BeautifulSoup

	APP_NAME   = 'MovieListr'
	API_KEY    = 'netflix_api_key'
	API_SECRET = 'netflix_api_secret'
	CALLBACK   = ''
	verbose = False

	# Lets get term from movie directory
	term = ''
	try:
		md = MovieDirectory.objects.all().order_by('-id')[0]
		page = md.page
		last_searched = md.counter
	except:
		# Didnt exist, lets create one
		page = 1
		last_searched = -1
		md = MovieDirectory(page = page, counter = last_searched)
		md.save()

	url = 'http://www.rottentomatoes.com/features/stats/index/%s.php' % str(page)

	fh = urllib2.urlopen(url)
	html = fh.read()
	fh.close()

	soup = BeautifulSoup(html)
	links = soup.findAll('a')

	titleTag = soup.html.head.title.string

	did_page = False

	if(re.search('Directory', titleTag)):
		curr_counter = 0
		next_counter = last_searched + 1
		for l in links:
			curr_title = l.contents
			if(curr_counter >= next_counter and curr_title != '' and len(curr_title) > 0):
				md.counter = curr_counter
				md.save()
				did_page = True
				term = curr_title[0]
				break
			curr_counter += 1
	else:
		# Wrong page, finished the whole thing
		md.delete()
		return direct_to_template(request, 'ajax.html', {'out':'Finished the whole list, restarting from the start'})

	if(not did_page):
		page += 1
		md.counter = 0
		md.page = page
		md.save()
		return direct_to_template(request, 'ajax.html', {'out':'Finished current page'})
	else:
		# Got something
		pass

	netflixClient = NetflixClient(APP_NAME, API_KEY, API_SECRET, CALLBACK, verbose)
	discs=[]
	data = doSearch(netflixClient,discs,term)

	out = ''

	for part in data:
		try:
			# Check if movie already exists
			link = part['id']
			link_parts = link.split('/')
			link_parts = link_parts[len(link_parts) - 1]
			link = 'http://www.netflix.com/Movie/' + link_parts
			try:
				alr_movie = Movie.objects.filter(link = link)[0]
			except:
				# Doesnt exist, go ahead
				curr_title = part['title']['regular']
				box_art_small = part['box_art']['small']
				box_art_medium = part['box_art']['medium']
				box_art_big = part['box_art']['large']
				release_year = int(part['release_year'])
				score = float(part['average_rating'])
				genres = []
				rating = ''
				cats = part['category']
				for cat in cats:
					if re.search('ratings', cat['scheme']):
						rating = cat['label']
					elif re.search('genres', cat['scheme']):
						genres.append(cat['label'])
				genres = ', '.join(genres)
				out += curr_title + ' --- \n'
				# Everything went ok, save movie
				new_movie = Movie(title = curr_title, box_art_small = box_art_small, box_art_medium = box_art_medium, box_art_big = box_art_big, release_year = release_year, rating = rating, genres = genres, link = link, score = score, owned_by = 0)
				new_movie.save()
		except:
			# Something went wrong, dont save movie
			out += 'Error in actual saving: ' + part['id'] + '\n'
	return direct_to_template(request, 'ajax.html', {'out':out})