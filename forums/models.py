from django.db import models
from django.contrib.auth.models import User
from django.utils.encoding import smart_unicode

class Category(models.Model):
	title = models.CharField(max_length=255)
	description = models.TextField()
	admin_only = models.BooleanField()
	
	def __unicode__(self):
		return self.title

class Thread(models.Model):
	category = models.ForeignKey(Category, related_name='thread_category')
	user = models.ForeignKey(User, related_name='thread_user')
	title = models.CharField(max_length=255)
	added = models.DateTimeField(auto_now_add=True)
	modded = models.DateTimeField(auto_now=True)
	
	def __unicode__(self):
		return self.category.title + ' : ' + smart_unicode(self.title) + ' : ' + smart_unicode(self.user.username)

class Message(models.Model):
	user = models.ForeignKey(User, related_name='message_user')
	thread = models.ForeignKey(Thread, related_name='message_thread')
	message = models.TextField()
	added = models.DateTimeField(auto_now_add=True)
	modded = models.DateTimeField(auto_now=True)
	
	def __unicode__(self):
		return smart_unicode(self.thread.title) + ' : ' + smart_unicode(self.user.username)