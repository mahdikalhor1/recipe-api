from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class UserMananger(BaseUserManager):

    def create(self, email, password=None, **extra_fields):

        user = self.model(email=self.normalize_email(email), **extra_fields)

        user.set_password(password)
        user.save(using=self._db)

        return user

class User(AbstractBaseUser):
    email = models.EmailField(max_length=300, unique=True)
    name = models.CharField(max_length=300)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD='email'

    objects = UserMananger()