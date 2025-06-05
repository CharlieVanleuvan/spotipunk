import praw
import re
import spotipy
from datetime import datetime, timezone, timedelta
from spotipy.oauth2 import SpotifyClientCredentials,SpotifyOAuth

from reddit_creds import client_id,client_secret,user_agent
from spotify_creds import spotify_client_id,spotify_client_secret,spotify_redirect_uri

from spotify_client import authenticate_spotify, remove_old_songs, current_playlist_songs, album_popular_songs, add_songs_to_playlist
from reddit_client import reddit_client

#spotipunk playlist id
playlist_id = '0bzaTO3nrX2Xidm7CZVtjP'

#call reddit_client to collect album tags and track tags
rc = reddit_client(subreddit='poppunkers',
                   period='week',
                   client_id=client_id,
                   client_secret=client_secret,
                   user_agent=user_agent)
albums,tracks = rc[0]['album_tag'], rc[1]['track_tag']

#connect to Spotify
sp = authenticate_spotify(client_id=spotify_client_id,
                          client_secret=spotify_client_secret,
                          redirect_uri=spotify_redirect_uri)

#remove old songs from playlist
remove_old_songs(playlist_id=playlist_id, sp=sp)

#get a set of songs currently in the playlist (to prevent duplicates)
current_songs = current_playlist_songs(playlist_id=playlist_id, sp=sp)

#grab popular song ids from album tags
for album_tag in albums:
    tracks.extend(album_popular_songs(album_id=album_tag, sp=sp))

# remove any song ids that already exist in the playlist
tracks = list(set(tracks) - current_songs)

#upload all tracks
add_songs_to_playlist(playlist_id=playlist_id,
                      items=tracks,
                      sp=sp)
