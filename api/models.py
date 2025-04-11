from django.db import models

from django.contrib.auth.models import (AbstractBaseUser, PermissionsMixin, BaseUserManager)

from uuid import uuid4

class UserManager(BaseUserManager):

    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The given email must be set')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password):
        user = self.create_user(email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save()
        return user



class User (AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    email = models.EmailField(unique=True)
    is_admin = models.BooleanField(default=False)
    username = models.CharField()

    USERNAME_FIELD = 'email'
    objects = UserManager()

class Game (models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    start_date = models.DateTimeField(auto_now_add=True)
    session_start = models.DateTimeField(auto_now_add=True)
    time_spend = models.IntegerField()
    hint_left = models.IntegerField()
    progress = models.IntegerField()
    game_code = models.IntegerField()
    status = models.CharField()
    p1 = models.ForeignKey('api.User', on_delete=models.CASCADE, related_name="game_as_p1")
    p2 = models.ForeignKey('api.User', on_delete=models.CASCADE, related_name="game_as_p2")

class Enigmes (models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    question_p1 = models.TextField()
    question_p2 = models.TextField()
    solution = models.TextField()
    hint = models.TextField()
    type = models.CharField()
    name = models.CharField()
    description = models.TextField()