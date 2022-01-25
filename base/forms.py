from dataclasses import fields
from django import forms
import imp
from pyexpat import model
from django.forms import ModelForm
from .models import Profile, Room
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class RoomForm(ModelForm):
    class Meta:
        model=Room
        fields = '__all__'
        exclude = ['host','participants']


class UserForm(ModelForm):
    class Meta:
        model=User
        fields=['username','email']
        
class userRegisterForm(UserCreationForm):

    email = forms.EmailField()

	
    class Meta:
        model = User
        fields = [
					'first_name',
					'last_name',
					'username',
					'email',
					'password1',
					'password2',
				]

class profileEditForm(ModelForm):

    

	
    class Meta:
        model = Profile
        fields = [
					'bio',
					'avatar',
				]

