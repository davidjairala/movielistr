from django.http import HttpResponseRedirect
from django.views.generic.simple import direct_to_template
from django.db.models import Q
from movielistr.forums.models import *
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from django.core.mail import mail_admins

# Forums index
def index(request):
	cats = Category.objects.all().order_by('title')
	return direct_to_template(request, 'forums/index.html', { 'cats':cats })

# View thread
def view_thread(request, cat_id, thread_id):
	try:
		err = None
		try:
			info = request.GET['info']
		except:
			info = None
		pagesize = 20
		try:
			pnum = int(request.GET['page'])
		except:
			pnum = 1
		category = Category.objects.get(pk=cat_id)
		thread = Thread.objects.get(pk=thread_id)
		# Save new message
		if(request.POST):
			message = request.POST['message']
			try:
				user = User.objects.get(pk=request.POST['cheat_user'])
			except:
				user = request.user
			new_message = Message(user = user, thread = thread, message = message)
			new_message.save()
			mail_admins('MovieListr - New forum message', 'New message in MovieListr:\n\nhttp://movielistr.com/forums/' + str(category.id) + '/' + str(thread.id) + '/\n\nUser:\n' + user.username + '\n\nTopic:\n' + thread.title + '\n\nMessage:\n' + new_message.message, fail_silently=True)
			info = 'added_msg'
		msgs = Message.objects.filter(thread=thread).order_by('id')
		p = Paginator(msgs, pagesize)
		p = p.page(pnum)
		staff_users = None
		if(request.user.is_staff):
			staff_users = User.objects.filter(is_staff=True).order_by('username')
		return direct_to_template(request, 'forums/view_thread.html', { 'category':category, 'thread':thread, 'msgs':p, 'pnum':pnum, 'info':info, 'err':err, 'staff_users':staff_users })
	except:
		return direct_to_template(request, 'err_404.html', {  })

# View category
def view_cat(request, cat_id):
	try:
		pagesize = 20
		try:
			pnum = int(request.GET['page'])
		except:
			pnum = 1
		category = Category.objects.get(pk=cat_id)
		threads = Thread.objects.filter(category=category).order_by('-id')
		p = Paginator(threads, pagesize)
		p = p.page(pnum)
		return direct_to_template(request, 'forums/view_cat.html', { 'category':category, 'threads':p, 'pnum':pnum })
	except:
		return direct_to_template(request, 'err_404.html', {  })

# Add thread
def add_thread(request, cat_id):
	try:
		category = Category.objects.get(pk=cat_id)
		if(not category.admin_only or (category.admin_only and request.user.is_staff)):
			err = None
			if(request.POST):
				title = request.POST['title']
				message = request.POST['message']
				if(title != '' and message != ''):
					try:
						user = User.objects.get(pk=request.POST['cheat_user'])
					except:
						user = request.user
					new_thread = Thread(category = category, user = user, title = title)
					new_thread.save()
					new_message = Message(user = user, thread = new_thread, message = message)
					new_message.save()
					mail_admins('MovieListr - New thread', 'New thread in MovieListr:\n\nhttp://movielistr.com/forums/' + str(category.id) + '/' + str(new_thread.id) + '/\n\nUser:\n' + user.username + '\n\nTopic:\n' + new_thread.title + '\n\nMessage:\n' + new_message.message, fail_silently=True)
					return HttpResponseRedirect('/forums/' + cat_id + '/' + str(new_thread.id) + '/?info=added')
				else:
					err = 'Please fill in the title and message fields.'
			staff_users = None
			if(request.user.is_staff):
				staff_users = User.objects.filter(is_staff=True).order_by('username')
			return direct_to_template(request, 'forums/add_thread.html', { 'category':category, 'staff_users':staff_users, 'err':err })
		else:
			return direct_to_template(request, 'err_perms.html', {  })
	except:
		return direct_to_template(request, 'err_404.html', {  })