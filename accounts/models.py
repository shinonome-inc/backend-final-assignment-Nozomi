from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField()


class FriendShip(models.Model):
    following = models.ForeignKey(User, related_name="follower_friendships", on_delete=models.CASCADE)
    follower = models.ForeignKey(User, related_name="following_friendships", on_delete=models.CASCADE)

    def __str__(self):
        return self.username
