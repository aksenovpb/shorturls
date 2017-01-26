from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import AbstractUser

# Create your models here.
class AccountManager(BaseUserManager):
    def create_user(self, email, password=None, **kwargs):
        if not email:
            raise ValueError('Users must have a valid email address')

        if not kwargs.get('username'):
            raise ValueError('Users must have a valid username')

        account = self.model(email=self.normalize_email(email),
                username=kwargs.get('username')) 

        account.set_password(password)
        user.save(using=self._db)

        return account

    def create_superuser(self, email, password, **kwargs):
        account = self.create_user(email, password, **kwargs)

        account.is_superuser = True
        account.save()

        return account


class Account(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=40)

    objects = AccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS =['username']

    def __unicode__(self):
        return self.email

    def __str__(self):
        return self.email
