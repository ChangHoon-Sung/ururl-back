from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

# Create your models here.

class UserManager(BaseUserManager):
    def create_user(self, username, password):
        if not username:
            raise ValueError("Username is required")
        
        user: User = self.model(username=username)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password):
        user: User = self.create_user(username, password)

        user.is_superuser = True
        user.save(using=self._db)
        return user
    

class User(AbstractUser):
    objects = UserManager()
    
    is_staff = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)    

    REQUIRED_FIELDS = []
