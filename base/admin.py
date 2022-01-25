from django.contrib import admin

# Register your models here.
from .models import Room,Topic,message,Profile

admin.site.register(Room)
admin.site.register(Topic)
admin.site.register(message)
admin.site.register(Profile)
