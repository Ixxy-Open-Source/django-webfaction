try:
    from django.conf.urls import *
except:
    from django.conf.urls import *

urlpatterns = patterns('django-webfaction.views',  
    url(r'^email/add/$', 'email_changeform'),
    url(r'^email/(?P<id>\d+)/$', 'email_changeform'),
    url(r'^email/$', 'email_changelist'),
)
