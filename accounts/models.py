from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField()


class Friends(models.Model):
    following = models.ForeignKey(User, related_name="follower", on_delete=models.CASCADE)
    follower = models.ForeignKey(User, related_name="following", on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username
