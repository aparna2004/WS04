from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.conf import settings
import requests
from .utils import get_spotify_token
import base64
import json


def spotify_login(request):
    scope = 'user-read-private playlist-modify-public playlist-modify-private'
    auth_url = f'https://accounts.spotify.com/authorize?client_id={settings.SPOTIFY_CLIENT_ID}&response_type=code&redirect_uri={settings.SPOTIFY_REDIRECT_URI}&scope={scope}'
    return redirect(auth_url)


def spotify_callback(request):
    code = request.GET.get('code')

    auth_header = base64.b64encode(
        f"{settings.SPOTIFY_CLIENT_ID}:{settings.SPOTIFY_CLIENT_SECRET}".encode()
    ).decode()

    response = requests.post('https://accounts.spotify.com/api/token', data={
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': settings.SPOTIFY_REDIRECT_URI,
    }, headers={'Authorization': f'Basic {auth_header}'})

    data = response.json()

    token = SpotifyToken.objects.create(
        user=request.user,
        access_token=data['access_token'],
        refresh_token=data['refresh_token'],
        expires_in=timezone.now() + timedelta(seconds=data['expires_in'])
    )

    return redirect('search')


@login_required
def search_view(request):
    query = request.GET.get('q', '')
    results = {}

    if query:
        token = get_spotify_token(request.user)
        if token:
            headers = {'Authorization': f'Bearer {token}'}
            response = requests.get(
                f'https://api.spotify.com/v1/search?q={query}&type=track,album,artist',
                headers=headers
            )
            results = response.json()

    return render(request, 'spotify_app/search.html', {'results': results})


@login_required
def album_detail(request, album_id):
    token = get_spotify_token(request.user)
    if token:
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(
            f'https://api.spotify.com/v1/albums/{album_id}',
            headers=headers
        )
        album_data = response.json()
        return render(request, 'spotify_app/album_detail.html', {'album': album_data})
    return redirect('spotify_login')


@login_required
def add_to_playlist(request, playlist_id):
    if request.method == 'POST':
        track_uris = request.POST.getlist('tracks')
        token = get_spotify_token(request.user)

        if token and track_uris:
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }

            data = {'uris': track_uris}
            response = requests.post(
                f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks',
                headers=headers,
                data=json.dumps(data)
            )

            if response.status_code == 201:
                return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error'})


