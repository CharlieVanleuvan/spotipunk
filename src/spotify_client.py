import spotipy
from datetime import datetime, timezone, timedelta
from spotipy.oauth2 import SpotifyClientCredentials,SpotifyOAuth
from spotify_creds import spotify_client_id,spotify_client_secret,spotify_redirect_uri

def authenticate_spotify(client_id: str, 
                         client_secret: str,
                         redirect_uri: str):
    """
    Authenticate with Spotify
    """
    scope = 'playlist-modify-public user-library-read'
    try:
        sp_oauth = SpotifyOAuth(
            scope=scope,
            redirect_uri=spotify_redirect_uri,
            client_id=spotify_client_id,
            client_secret=spotify_client_secret,
            cache_path='.spotify_cache'
        )

        # Attempt to get a token from cache or prompt for a new one
        token_info = sp_oauth.get_cached_token()

        if not token_info:
            print("No cached token found. Initiating new authentication flow...")
            # This will open a browser window for the user to log in and authorize
            # It will then redirect to the REDIRECT_URI specified.
            # Spotipy will automatically capture the authorization code from the URL
            # and exchange it for an access token.
            token_info = sp_oauth.get_access_token(code=None) # Passing code=None tells it to use the redirect flow

        if token_info:
            print("Authentication successful!")
            return spotipy.Spotify(auth=token_info['access_token'])
        else:
            print("Authentication failed: Could not retrieve access token.")
            return None

    except Exception as e:
        print(f"An error occurred during authentication: {e}")
        print("Please ensure your SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, and SPOTIPY_REDIRECT_URI environment variables are set correctly.")
        print("Also, double-check that your Redirect URI in the Spotify Developer Dashboard matches your code exactly.")
        return None    


def remove_old_songs(playlist_id: str,
                     sp: object) -> None:
    """
    Remove songs from the playlist that were added more than 30 days ago
    """
    removed_songs_counter = 0
    playlist_details = sp.playlist(playlist_id=playlist_id,additional_types=['track'])
    for track in playlist_details['tracks']['items']:
        track_timestamp = track['added_at']
        track_timestamp = datetime.strptime(track_timestamp.replace('Z',''), '%Y-%m-%dT%H:%M:%S').replace(tzinfo=timezone.utc)
        if track_timestamp < (datetime.now(tz=timezone.utc)-timedelta(days=30)):
            track_id = track['track']['id']
            sp.playlist_remove_all_occurrences_of_items(playlist_id=playlist_id,items=[track_id])
            removed_songs_counter += 1
    
    print(f"Removed {removed_songs_counter} songs")
    return None

def current_playlist_songs(playlist_id: str,
                           sp: object) -> set:
    """
    Get the IDs of the songs currently in the playlist.
    This is used to check if a song is already present in the playlist, to prevent duplication
    """
    playlist_details = sp.playlist(playlist_id=playlist_id,additional_types=['track'])
    track_ids = set([track['track']['id'] for track in playlist_details['tracks']['items']])
    return track_ids

def album_popular_songs(album_id:str,
                        sp: object) -> list:
    """
    Get up to the 3 most popular songs from an album.
    If there is a single most popular song, only that song will be collected
    Otherwise, if there is a tie for popularity, up to 3 songs will be collected
    """
    album_details = sp.album_tracks(album_id=album_id,market='US')
    album = sp.album(album_id=album_id, market='US')
    album_name = album['name']
    artist_name = [artist['name'] for artist in album['artists']]
    track_uris = [track['uri'] for track in album_details['items']]
    max_popularity = 0
    most_popular_song_ids = []
    for uri in track_uris:
        track_details = sp.track(track_id=uri)
        if track_details['popularity'] > max_popularity:
            max_popularity = track_details['popularity']
            most_popular_song_ids = []
            most_popular_song_ids.append(track_details['id'])
        elif track_details['popularity'] == max_popularity:
            most_popular_song_ids.append(track_details['id'])
        else:
            continue
    print(f"Grabbing {len(most_popular_song_ids[:3])} songs from album '{album_name}' by {' and '.join(artist_name)}")
    return most_popular_song_ids[:3]

def add_songs_to_playlist(playlist_id: str,
                          items:list,
                          sp: object) -> None:
    """
    Add songs to the playlist
    """
    number_of_songs = len(items)
    try:
        sp.playlist_add_items(playlist_id=playlist_id,items = items)
        print(f"Added {number_of_songs} songs to the playlist")
    except Exception as e:
        print(f"An error occurred while adding songs: {e}")
    return None
