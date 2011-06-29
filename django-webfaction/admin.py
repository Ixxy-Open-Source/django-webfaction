from django.contrib.admin.sites import AlreadyRegistered
from django.contrib import admin
from django.conf import settings

from models import Email
from models import Log

class EmailOptions (admin.ModelAdmin):
    name="Email"

class LogOptions (admin.ModelAdmin):
    name="Email"
    list_display = ('action', 'user', 'timestamp', )
    list_filter = ('user', 'timestamp', )
    
try:
    admin.site.register(Email, EmailOptions)
    admin.site.register(Log, LogOptions)
except AlreadyRegistered:
    pass