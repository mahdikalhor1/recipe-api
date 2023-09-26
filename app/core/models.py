from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import MinValueValidator
import app.settings as settings
class UserMananger(BaseUserManager):

    def create(self, email, password=None, **extra_fields):

        if not email:
            raise ValueError
        
        user = self.model(email=self.normalize_email(email), **extra_fields)

        user.set_password(password)
        user.save(using=self._db)

        return user


    def create_superuser(self, email, password):
        user = self.create(email, password)

        user.is_staff = True
        user.is_superuser = True

        user.save(using=self._db)

        return user
    


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=300, unique=True)
    name = models.CharField(max_length=300)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD='email'

    objects = UserMananger()


class Recipe(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    title = models.CharField(max_length=50)
    time_minute = models.IntegerField(validators=[MinValueValidator(0)])
    price = models.DecimalField(decimal_places=2,max_digits=6,
                                validators=[MinValueValidator(0)])
    description = models.TextField(blank=True)
    link = models.CharField(max_length=200, null=True)

    def __str__(self):
        return self.title
    
class Tag(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)

    def __str__(self):
        return self.name