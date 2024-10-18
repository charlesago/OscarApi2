import hashlib
import secrets
import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Model



class CustomUser(AbstractUser):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    enabled = models.BooleanField(default=False)

    def __str__(self):
        return self.username


class Author(models.Model):
    name = models.CharField(max_length=100)
    firstName = models.CharField(max_length=100)
    birthDate = models.DateField()

class Genre(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    def __str__(self):
        return self.name


class Movie(models.Model):
    title = models.CharField(max_length=100)
    publishedDate = models.DateField()
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    genre = models.ManyToManyField(Genre)
    creator = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class GlobalApiKey(models.Model):
    key = models.CharField(max_length=256, unique=True, editable=False)
    name = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    @staticmethod
    def generate_raw_key():

        return secrets.token_urlsafe(50)

    @staticmethod
    def hash_key(raw_key):

        return hashlib.sha256(raw_key.encode('utf-8')).hexdigest()

    def check_key(self, raw_key):
        return self.key == self.hash_key(raw_key)

class Client(models.Model):
    client_id = models.CharField(max_length=255, unique=True)
    email = models.CharField(max_length=255)
    api_key = models.CharField(max_length=256, unique=True)
    count = models.IntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    uuid = models.CharField(max_length=36, blank=True, null=True, unique=True)

    def __str__(self):
        return f"{self.email} ({self.client_id})"