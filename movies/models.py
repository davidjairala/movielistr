from django.db import models
from django.utils.encoding import smart_unicode
from django.contrib.auth.models import User

class Movie(models.Model):
	title = models.CharField(max_length=500)
	box_art_small = models.CharField(max_length=255)
	box_art_medium = models.CharField(max_length=255)
	box_art_big = models.CharField(max_length=255)
	release_year = models.IntegerField()
	rating = models.CharField(max_length=255)
	genres = models.CharField(max_length=500)
	link = models.CharField(max_length=255)
	score = models.FloatField()
	added = models.DateTimeField(auto_now_add=True)
	modded = models.DateTimeField(auto_now=True)
	owned_by = models.IntegerField()
	
	def __unicode__(self):
		return smart_unicode(self.title) + ' : ' + str(self.release_year)
	
	# Checks if a user has a movie
	def hasMovie(self, user):
		if(user.is_authenticated()):
			try:
				mu = MovieUser.objects.filter(user = user, movie = self)[0]
				return True
			except:
				pass
	
	# Checks if user has movie on wishlist
	def hasWishlist(self, user):
		if(user.is_authenticated()):
			try:
				mu = Wishlist.objects.filter(user = user, movie = self)[0]
				return True
			except:
				pass
	
	# Returns a short title for the movie
	def short_title(self):
		size = 30
		if(len(self.title) > 30):
			return smart_unicode(self.title[0:30]) + '...'
		else:
			return smart_unicode(self.title)
	
	# Returns genres linked
	def link_genres(self):
		import urllib
		genres = self.genres
		genres_arr = genres.split(',')
		genres_out = []
		for gen in genres_arr:
			gen_org = gen
			gen = gen.strip()
			gen = urllib.quote(gen)
			if(gen != ''):
				genres_out.append('<a href="/movies/?q=' + gen + '">' + gen_org + '</a>')
		return ' &#183; '.join(genres_out)
	
	# Checks if the movie has a trailer
	def has_trailer(self):
		try:
			trailer = Trailer.objects.filter(movie = self)[0]
			return trailer
		except:
			pass

class MovieDirectory(models.Model):
	page = models.IntegerField()
	counter = models.IntegerField()
	
	def __unicode__(self):
		return str(self.page) + ' : ' + str(self.counter)

class MovieUser(models.Model):
	user = models.ForeignKey(User, related_name='mu_user')
	movie = models.ForeignKey(Movie, related_name='mu_movie')
	location = models.CharField(max_length=500)
	notes = models.TextField(blank=True, null=True)
	added = models.DateTimeField(auto_now_add=True)
	modded = models.DateTimeField(auto_now=True)
	
	def __unicode__(self):
		return smart_unicode(self.user.username) + ' : ' + smart_unicode(self.movie)
	
	# Returns linked string for location
	def link_location(self):
		location = self.location
		location_arr = location.split(',')
		loc_out = []
		for loc in location_arr:
			loc = loc.strip()
			if(loc != ''):
				loc_out.append('<a href="/search_location/?loc=' + loc + '">' + loc + '</a>')
		return ' &#183; '.join(loc_out)

class Wishlist(models.Model):
	user = models.ForeignKey(User, related_name='wl_user')
	movie = models.ForeignKey(Movie, related_name='wl_movie')
	added = models.DateTimeField(auto_now_add=True)
	modded = models.DateTimeField(auto_now=True)
	
	def __unicode__(self):
		return smart_unicode(self.user.username) + ' : ' + smart_unicode(self.movie)

class Location(models.Model):
	user = models.ForeignKey(User, related_name='location_user')
	tag = models.CharField(max_length=255)
	added = models.DateTimeField(auto_now_add=True)
	modded = models.DateTimeField(auto_now=True)
	
	def __unicode__(self):
		return smart_unicode(self.user.username) + ' : ' + smart_unicode(self.tag)

class Trailer(models.Model):
	movie = models.ForeignKey(Movie, related_name='trailer_movie')
	link = models.CharField(max_length=255)
	
	def __unicode__(self):
		return smart_unicode(self.movie) + ' : ' + self.link
	
	# Returns the trailer stub - the id for youtube videos
	def trailer_stub(self):
		try:
			link = self.link
			link = link.split('?v=')
			link = link[1]
			link = link.split('&feature')
			link = link[0]
			return link
		except:
			pass

class TrailerLastSearched(models.Model):
	movie = models.ForeignKey(Movie, related_name='ls_movie')
	
	def __unicode__(self):
		return smart_unicode(self.movie)

class Comment(models.Model):
	movie = models.ForeignKey(Movie, related_name='comment_movie')
	user = models.ForeignKey(User, related_name='comment_user')
	comment = models.TextField()
	added = models.DateTimeField(auto_now_add=True)
	modded = models.DateTimeField(auto_now=True)
	
	def __unicode__(self):
		return smart_unicode(self.user.username) + ' : ' + smart_unicode(self.movie.title) + ' : ' + smart_unicode(self.comment)

class Related(models.Model):
	movie = models.ForeignKey(Movie, related_name='related_movie')
	related = models.ForeignKey(Movie, related_name='related_related')
	
	def __unicode__(self):
		return smart_unicode(self.movie.title) + ' : ' + smart_unicode(self.related.title)

class LastRelated(models.Model):
	movie = models.ForeignKey(Movie, related_name='last_related_movie')
	
	def __unicode__(self):
		return smart_unicode(self.movie.title)