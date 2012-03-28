from django.db import models
from django.utils.encoding import smart_unicode
from django.contrib.auth.models import User

class Friend(models.Model):
	user = models.ForeignKey(User, related_name='friend_user')
	friend = models.ForeignKey(User, related_name='friend_friend')
	
	def __unicode__(self):
		return smart_unicode(self.user.username) + ' : ' + smart_unicode(self.friend.username)