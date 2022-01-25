
from email.policy import default
from django.db import models

from django.contrib.auth.models import User

# Create your models here.
class Topic(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Room(models.Model):
    host =models.ForeignKey(User, on_delete=models.SET_NULL,null=True)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL,null=True)
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    participants = models.ManyToManyField(User,related_name='participants',blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering= ['-updated','-created']

    def __str__(self) :
        return self.name    


class message(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    body = models.TextField()
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering= ['-updated','-created']

    def __str__(self):
        return self.body[0:50]

#to make the email field for auth.User unique
#User._meta.get_field('email')._unique = True

class Profile(models.Model):
    user= models.OneToOneField(User,on_delete=models.CASCADE)
    bio = models.TextField(null=True, blank=True)
    avatar= models.ImageField(null=True,default='avatar.svg')

    def __str__(self):
        return f'{self.user.username} Profile'