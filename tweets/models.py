from django.db import models

from accounts.models import User


class Tweet(models.Model):
    content = models.CharField(max_length=150)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content


class Like(models.Model):
    tweet = models.ForeignKey(Tweet, on_delete=models.CASCADE, related_name="liked_tweet")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="liked_user")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["tweet", "user"], name="unique_like"),
        ]
