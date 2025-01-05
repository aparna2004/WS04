import requests
from datetime import timedelta
from django.utils import timezone
from .models import SpotifyToken


def get_spotify_token(user):
    token = SpotifyToken.objects.filter(user=user).first()
    if token and token.is_expired():
        refresh_spotify_token(token)
    return token.access_token if token else None


def refresh_spotify_token(token):
    response = requests.post('https://accounts.spotify.com/api/token', data={
        'grant_type': 'refresh_token',
        'refresh_token': token.refresh_token,
        'client_id': settings.SPOTIFY_CLIENT_ID,
        'client_secret': settings.SPOTIFY_CLIENT_SECRET,
    })

    data = response.json()
    token.access_token = data['access_token']
    token.expires_in = timezone.now() + timedelta(seconds=data['expires_in'])
    token.save()
