try:
    from django.conf.urls.defaults import *
except:
    from django.conf.urls import *

urlpatterns = patterns('django_webfaction_email.views',  
    url(r'^email/add/$', 'email_changeform'),
    url(r'^email/(?P<id>\d+)/$', 'email_changeform'),
    url(r'^email/$', 'email_changelist'),
)
