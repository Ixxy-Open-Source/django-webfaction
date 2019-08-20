from django.conf.urls import url
import django_webfaction_email.views

urlpatterns = [
    url(r'^email/add/$', django_webfaction_email.views.email_changeform),
    url(r'^email/(?P<id>\d+)/$', django_webfaction_email.views.email_changeform),
    url(r'^email/$', django_webfaction_email.views.email_changelist),
]
