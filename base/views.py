from email import message_from_binary_file
import imp
from multiprocessing import context
from os import name
from urllib import request
from .models import Room,Topic,message,Profile
from .forms import userRegisterForm,profileEditForm

from django.http import HttpResponse
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.shortcuts import render,redirect
from .forms import RoomForm,UserForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout

""" rooms= [
    {'id':1, 'name':'lets learn python' },
    {'id':2, 'name':'design with me' },
    {'id':3, 'name':'frontend dev' },
]
 """
# Create your views here.
def loginPage(request):
    page= 'login'
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username= request.POST.get('username').lower()
        password = request.POST.get('password')

        try:
            user= User.objects.get(username=username)

        except :
            messages.error(request,'user does not exist!')

        user = authenticate(request,username=username,password=password)

        if user is not None:
            login(request,user)
            return redirect('home')
        else:
            messages.error(request,'username or password does not exist!')


    context={'page':page}
    return render(request, 'base/login_register.html',context)


def logoutUser(request):
    logout(request)
    return redirect('home')



def registerPage(request):
    form = userRegisterForm()
    if request.method == 'POST':
        form =userRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            
            user.save()
            Profile.objects.create(
                user=user
            )
            login(request,user)
            return redirect('home')

        else:
            messages.error(request,'an error occured during registartion')
        
        
    context={'form':form}
    return render(request,'base/login_register.html',context)



def home(request):
    q=request.GET.get('q') if request.GET.get('q') != None else ''
    rooms=Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )
    topics=Topic.objects.all()[0:5]
    room_count = rooms.count()
    room_messages = message.objects.filter(
        Q(room__topic__name__icontains=q)
    )

    context= {'rooms':rooms,'topics':topics,
    'room_count':room_count,'room_messages':room_messages }
    return render(request, 'base/home.html',context)


def room(request,pk):
    room=Room.objects.get(id=pk)
    
    room_messages=room.message_set.all().order_by('-created')
    participants = room.participants.all()
    if request.method == 'POST':
        
        messages= message.objects.create(
            user= request.user,
            room=room,
            body= request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)

    
    
    context={'room':room, 'room_messages': room_messages,'participants':participants}
    return render(request, 'base/room.html',context)



@login_required(login_url='login')
def createRoom(request):
    form= RoomForm()
    topics=Topic.objects.all()
    if request.method == 'POST':
        topic_name=request.POST.get('topic')
        topic, created=Topic.objects.get_or_create(name=topic_name)
        Room.objects.create(
           host= request.user,
           topic=topic,
           name=request.POST.get('name'),
           description=request.POST.get('description'),

       )
        return redirect('home')

        """ form= RoomForm(request.POST)
        if form.is_valid():
            room= form.save(commit=False)
            room.host = request.user
            room.save() """
            

    context= {'form':form,'topics':topics}
    return render(request,"base/room_form.html",context)

@login_required(login_url='login')
def updateRoom(request, pk):
    room= Room.objects.get(id=pk)
    form= RoomForm(instance=room)
    topics=Topic.objects.all()
    if request.user != room.host:
        return HttpResponse('you are not allowed here')

    if request.method == 'POST':
        topic_name=request.POST.get('topic')
        topic, created=Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')

    update=True
    context= {'form':form,'topics':topics,'update':update}
    return render(request,"base/room_form.html", context)
    
@login_required(login_url='login')
def deleteRoom(request,pk):
    room= Room.objects.get(id=pk)
    if request.user != room.host:
        return HttpResponse('you are not allowed here')
    if request.method == 'POST' :
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html',{'obj':room})

@login_required(login_url='login')
def deleteMessage(request,pk):
    msg= message.objects.get(id=pk)
    if request.user != msg.user:
        return HttpResponse('you are not allowed here')
    if request.method == 'POST' :
        msg.delete()
        return redirect('home')
    return render(request, 'base/delete.html',{'obj':msg})


def userProfile(request,pk):
    user= User.objects.get(id=pk)
    profile=  Profile.objects.get(user=user)
    rooms=user.room_set.all()
    room_message = user.message_set.all()
    topics = Topic.objects.all()

    context={'user':user,
    'rooms':rooms,
    'room_messages':room_message,
    'topics':topics,
    'profile':profile
    }
    return render(request,'base/profile.html',context)
@login_required(login_url='login')
def updateUser(request):
    user=request.user
    form=UserForm(instance=user)
    if request.method == 'POST':
        form= UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile',pk=user.id)
    context={'form':form}
    return render(request, 'base/update-user.html',context)


def topicPage(request):
    
    q=request.GET.get('q') if request.GET.get('q') != None else ''
    topics= Topic.objects.filter(name__icontains=q)
    context={'topics':topics}
    return render(request,'base/topics.html',context)

def activityPage(request):
    room_messages= message.objects.all()
    context={'room_messages':room_messages}
    return render(request,'base/activity.html',context)


def editPrfilePage(request):
    form = profileEditForm()
    user=request.user
    form=profileEditForm(instance=user.profile)
    if request.method == 'POST':
        form=profileEditForm(request.POST, request.FILES,instance=user.profile )
        if form.is_valid():
            form.save()
            return redirect('user-profile',pk=user.id)
    context={'form':form}
    return render(request, 'base/edit_profile.html',context)