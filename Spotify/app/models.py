from django.db import models
from django.contrib.auth.models import User


class SpotifyToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    access_token = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=255)
    expires_in = models.DateTimeField()

    def is_expired(self):
        from django.utils import timezone
        return self.expires_in <= timezone.now()