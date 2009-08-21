from django.conf.urls.defaults import *

urlpatterns = patterns('django_webfaction.views',  
    url(r'^email/add/$', 'email_changeform'),
    url(r'^email/(?P<id>\d+)/$', 'email_changeform'),
    url(r'^email/$', 'email_changelist'),
)
