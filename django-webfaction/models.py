from django.db import models

from django.contrib.auth.models import User

class Email(models.Model):
    class Meta:
        verbose_name = "Email Address"
        verbose_name_plural = "Email Addresses"
        managed = False #Requires Django 1.1

class Log(models.Model):
    user = models.ForeignKey(User)
    action = models.TextField(max_length=256)
    timestamp = models.DateTimeField(auto_now_add=True)
    def __unicode__(self):
        return self.action