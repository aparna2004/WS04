# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.spotify_login, name='spotify_login'),
    path('callback/', views.spotify_callback, name='spotify_callback'),
    path('search/', views.search_view, name='search'),
    path('album/<str:album_id>/', views.album_detail, name='album_detail'),
    path('playlist/<str:playlist_id>/add/', views.add_to_playlist, name='add_to_playlist'),
]