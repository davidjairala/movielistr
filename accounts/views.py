from django.http import HttpResponse
from django.http import HttpResponsePermanentRedirect
from django.views.generic.simple import direct_to_template
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.models import User
from django.core.mail import send_mail, mail_admins
from django.db import models
from django.contrib.sites.models import Site
from django.db.models import Q
from django.core.paginator import Paginator
from random import Random
import string
from django.conf import settings
from movielistr.movies.models import *
from movielistr.accounts.models import *

# User search
def user_search(request):
	import re
	pagesize = 24
	try:
		pnum = int(request.GET['page'])
	except:
		pnum = 1
	q = None
	slink = None
	p = None
	exact = None
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
			users = User.objects.filter(Q(username__iregex=qs) | Q(email__iregex=qs)).order_by('username')
			slink = '&q=%s' % (q)
			p = Paginator(users, pagesize)
			p = p.page(pnum)
		else:
			users = None
	except:
		users = None

	return direct_to_template(request, 'accounts/user_search.html', { 'pnum':pnum, 'users':p, 'slink':slink, 'exact':exact, 'q':q })

# Show user stats image
def img_stats(request, user_id):
	from django.core.cache import cache
	import Image
	import ImageFont
	import ImageDraw
	import StringIO

	v_user = User.objects.get(pk=user_id)

	cache_name = 'stats_' + user_id
	gcache = cache.get(cache_name)

	if(gcache):
		return HttpResponse(gcache, mimetype="image/png")
	else:
		# Owned movies
		try:
			mus = MovieUser.objects.filter(user = v_user)
			movies_owned = len(mus)
		except:
			movies_owned = 0
		# Movies in wishlist
		try:
			wl = Wishlist.objects.filter(user = v_user)
			movies_wishlist = len(wl)
		except:
			movies_wishlist = 0
		# General score
		total_score = 0
		if(mus and len(mus) > 0 and movies_owned > 0):
			for mu in mus:
				total_score += mu.movie.score
			avg_score = total_score / movies_owned
			avg_score = "%.2f" % avg_score
		else:
			avg_score = 'N/A'

		# Create image
		font = ImageFont.truetype(settings.MEDIA_ROOT + '/fonts/arial.ttf', 11)
		im = Image.open(settings.MEDIA_ROOT + '/imgs/stats.png')
		draw = ImageDraw.Draw(im)
		draw.text((10, 45), "%(username)s's stats:" % { 'username':v_user.username }, font=font, fill="black")
		draw.text((10, 57), "%(movies_owned)s movies in library" % { 'movies_owned':str(movies_owned) }, font=font, fill="black")
		draw.text((10, 69), "%(movies_wishlist)s movies in wish list" % { 'movies_wishlist':str(movies_wishlist) }, font=font, fill="black")
		draw.text((10, 81), "Average score: %(avg_score)s" % { 'avg_score':str(avg_score) }, font=font, fill="black")

		out = StringIO.StringIO()
		im.save(out, 'PNG')
		cache.set(cache_name, out.getvalue(), settings.CACHETIME)
		out.close()

		response = HttpResponse(mimetype="image/png")
		im.save(response, "PNG")
		return response

# Add or remove friend
def toggle_friend(request, user_id):
	if(request.user.is_authenticated()):
		try:
			f_user = User.objects.get(pk=user_id)
			try:
				friend = Friend.objects.filter(user = request.user, friend = f_user)[0]
				# Already friends, remove
				friend.delete()
				return direct_to_template(request, 'ajax.html', { 'out':'removed' })
			except:
				# Not yet friends, add
				new_friend = Friend(user = request.user, friend = f_user)
				new_friend.save()
				return direct_to_template(request, 'ajax.html', { 'out':'added' })
		except:
			return direct_to_template(request, 'ajax.html', { 'out':'err_no_user' })
	else:
		return direct_to_template(request, 'ajax.html', { 'out':'err_login' })

# View user account
def view_user(request, user_id):
	try:
		view_user = User.objects.get(pk=user_id)
		# Are friends?
		are_friends = False
		try:
			friend = Friend.objects.filter(user = request.user, friend = view_user)[0]
			are_friends = True
		except:
			pass
		# Owned movies
		try:
			mus = MovieUser.objects.filter(user = view_user)
			movies_owned = len(mus)
		except:
			movies_owned = 0
		# Movies in wishlist
		try:
			wl = Wishlist.objects.filter(user = view_user)
			movies_wishlist = len(wl)
		except:
			movies_wishlist = 0
		# General score
		total_score = 0
		if(mus and len(mus) > 0 and movies_owned > 0):
			for mu in mus:
				total_score += mu.movie.score
			avg_score = total_score / movies_owned
			avg_score = "%.2f" % avg_score
		else:
			avg_score = False
		# Check if we should show social options
		if(request.user.is_authenticated() and view_user.id != request.user.id):
			show_social = True
		else:
			show_social = False
		return direct_to_template(request, 'accounts/view_user.html', { 'view_user':view_user, 'movies_owned':movies_owned, 'avg_score':avg_score, 'movies_wishlist':movies_wishlist, 'are_friends':are_friends, 'show_social':show_social })
	except:
		return direct_to_template(request, 'err_404.html', {  })

# My account
def account(request):
	if(request.user.is_authenticated()):
		# Friends
		friends = Friend.objects.filter(user = request.user).order_by('friend__username')
		# Owned movies
		try:
			mus = MovieUser.objects.filter(user = request.user)
			movies_owned = len(mus)
		except:
			movies_owned = 0
		# Movies in wishlist
		try:
			wl = Wishlist.objects.filter(user = request.user)
			movies_wishlist = len(wl)
		except:
			movies_wishlist = 0
		# General score
		total_score = 0
		if(mus and len(mus) > 0 and movies_owned > 0):
			for mu in mus:
				total_score += mu.movie.score
			avg_score = total_score / movies_owned
			avg_score = "%.2f" % avg_score
		else:
			avg_score = False
		return direct_to_template(request, 'accounts/account.html', { 'movies_owned':movies_owned, 'avg_score':avg_score, 'movies_wishlist':movies_wishlist, 'friends':friends })
	else:
		return direct_to_template(request, 'login_req.html', { 'next':'/account/' })

# Hace logout
def logout_view(request):
	logout(request)
	return direct_to_template(request, 'accounts/logout.html', {})

# Muestra forma de login
def login_view(request):
	try:
		next = request.GET['next']
	except:
		next = None
	return direct_to_template(request, 'accounts/login.html', {"btn":"login", 'next':next})

# Hace el login
def do_login(request):
	username = request.POST['username']
	password = request.POST['clave']
	user = authenticate(username=username, password=password)
	try:
		next = request.POST['next']
	except:
		next = None
	if user is not None:
		if user.is_active:
			login(request, user)
			return direct_to_template(request, 'accounts/logged.html', {'next':next})
		else:
			return direct_to_template(request, 'accounts/login.html', {"error":"This account has been blocked by the staff.","btn":"login", 'next':next})
	else:
		return direct_to_template(request, 'accounts/login.html', {"error":"Wrong username or password.","btn":"login", 'next':next})

# Muestra forma para registrarse
def register(request):
	try:
		next = request.GET['next']
	except:
		next = None
	return direct_to_template(request, 'accounts/register.html', {'next':next})

# Realiza el registro
def do_register(request):
	username = request.POST['username']
	password1 = request.POST['password1']
	password2 = request.POST['password2']
	email = request.POST['email']
	try:
		next = request.POST['next']
	except:
		next = None
	# Checamos que no exista el email
	try:
		user_alr = User.objects.filter(email=email)[0]
		return direct_to_template(request, 'accounts/register.html', {"error":"The email you have selected is already used by another account, please select another email.", 'next':next})
	except:
		if(username and password1 and password2 and email):
			if(password1 == password2):
				try:
					new_user = User(username=username, email=email)
					new_user.set_password(password1)
					new_user.is_staff = False
					new_user.is_superuser = False
					new_user.save()

					return direct_to_template(request, 'accounts/login.html', {"info":"Thanks for registering with MovieListr, please login with your username and password:", 'next':next})
				except:
					return direct_to_template(request, 'accounts/register.html', {"error":"The username you picked is already in use,, please pick another.", 'next':next})
			else:
				return direct_to_template(request, 'accounts/register.html', {"error":"The password and the password confirmation don't match, please try again.", 'next':next})
		else:
			return direct_to_template(request, 'accounts/register.html', {"error":"Please fill in all required fields.", 'next':next})

# Muestra forma para recuperar clave
def recover(request):
	return direct_to_template(request, 'accounts/recover.html', {})

# Envia mail con instrucciones para recuperar clave
def do_recover(request):
	email = request.POST['email']
	if(email):
		# Checamos si existe un usuario con ese email
		user = User.objects.filter(email=email)[:1]
		user = user[0]
		if(user):
			# Enviamos mail
			subject = 'MovieListr - Recover password'
			msg = 'Dear ' + user.username + ':\You have requested a password reset, to do so please follow this link:\n\nhttp://movielistr.com/post_recover/' + str(user.id) + ':' + user.password + '\n\n(If you have not requested a password reset, please ignore this email.)\n\nThanks,\nMovieListr\nhttp://movielistr.com'
			sfrom = 'info@movielistr.com'
			send_mail(subject, msg, sfrom, [user.email], fail_silently=True)
			return direct_to_template(request, 'accounts/do_recover.html', {})
		else:
			return direct_to_template(request, 'accounts/recover.html', {"error":"El e-mail no esta ligado a ninguna cuenta en el sistema."})
	else:
		return direct_to_template(request, 'accounts/recover.html', {"error":"Por favor introduce tu e-mail"})

# Realiza el proceso de reset de clave
def post_recover(request, shash):
	hash_arr = shash.split(':')
	user_id = hash_arr[0]
	pwd = hash_arr[1]
	users = User.objects.filter(password = pwd, id = user_id)
	new_pass = Random().sample(string.letters+string.digits, 6)
	new_pass = string.join(new_pass, '')
	if(users):
		for user in users:
			user.set_password(new_pass)
			user.save()
		return direct_to_template(request, 'accounts/post_recover.html', {"new_pass":new_pass})
	else:
		return direct_to_template(request, 'accounts/recover.html', {"error":"La liga que has introducido no es valida, por favor intenta nuevamente."})

# Muestra forma para cambiar clave
def chngpwd(request):
	return direct_to_template(request, 'accounts/chngpwd.html', {})

# Cambia clave para un usuario
def do_chngpwd(request):
	curr_pwd = request.POST['curr_pwd']
	new_pwd = request.POST['new_pwd']
	new_pwd2 = request.POST['new_pwd2']
	user_id = request.user.id
	if(curr_pwd and new_pwd and new_pwd2):
		# Buscamos al usuario con los datos introducidos
		user = User.objects.get(id=user_id)
		if(user):
			if(new_pwd == new_pwd2):
				user.set_password(new_pwd)
				user.save()
				return direct_to_template(request, 'accounts/do_chngpwd.html', {"new_pwd":new_pwd})
			else:
				return direct_to_template(request, 'accounts/chngpwd.html', {"error":"The new password and its confirmation do not match."})
		else:
			return direct_to_template(request, 'accounts/chngpwd.html', {"error":"We could not find a user with the specified data."})
	else:
		return direct_to_template(request, 'accounts/chngpwd.html', {"error":"Please fill in all the fields."})