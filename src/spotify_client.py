import re
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from datetime import datetime, timedelta, timezone
from src.config import AppConfig

def get_spotify_client() -> spotipy.Spotify:
    """
    Initializes a headless Spotipy client using the refresh token flow.
    Perfect for running unattended in Cloud Run.
    """
    auth_manager = SpotifyOAuth(
        client_id=AppConfig.SPOTIFY_CLIENT_ID,
        client_secret=AppConfig.SPOTIFY_CLIENT_SECRET,
        redirect_uri="https://localhost:8080",  # Placeholder required by Spotipy
        scope="playlist-modify-public playlist-modify-private",
        open_browser=False
    )
    
    # Force injection of our long-lived refresh token
    auth_manager.cache_handler.save_token_to_cache({
        "refresh_token": AppConfig.SPOTIFY_REFRESH_TOKEN,
        "access_token": "",
        "expires_at": 0
    })
    
    return spotipy.Spotify(auth_manager=auth_manager)


def get_current_playlist_tracks(sp: spotipy.Spotify, playlist_id: str) -> list[dict]:
    """
    Paginates through the entire Spotify playlist to extract all current tracks
    along with their 'added_at' timestamps.
    """
    tracks = []
    
    # Initial page request (caps at 100 items per Spotify API spec)
    results = sp.playlist_items(playlist_id, fields="items(added_at,track(id)),next")
    
    while results:
        for item in results.get('items', []):
            if item.get('track'):
                tracks.append({
                    "id": item['track']['id'],
                    "added_at": item['added_at']  # Format: "2026-05-10T14:20:00Z"
                })
        
        # Check if an additional page exists, and fetch it directly using the cursor URL
        if results.get('next'):
            results = sp.next(results)
        else:
            break
            
    return tracks


def extract_spotify_urls(raw_reddit_data: list[dict]) -> list[str]:
    """
    Parses raw Reddit post titles and comment bodies using regex 
    to extract matching Spotify URLs.
    """
    # Pattern captures open.spotify.com links for tracks, albums, or artists
    spotify_pattern = r'(https://open.spotify.com/(?:track|album|artist)/[a-zA-Z0-9?=&_-]+)'
    found_urls = set()
    
    for post in raw_reddit_data:
        # Check post title/URL
        for match in re.findall(spotify_pattern, post.get('title', '')):
            found_urls.add(match)
        if post.get('url') and 'spotify.com' in post['url']:
            found_urls.add(post['url'])
            
        # Check comments
        for comment in post.get('comments', []):
            for match in re.findall(spotify_pattern, comment.get('body', '')):
                found_urls.add(match)
                
    return list(found_urls)


def resolve_track_ids(sp: spotipy.Spotify, urls: list[str]) -> list[str]:
    """
    Takes raw URLs, identifies entity types, and resolves them to track IDs.
    If an album is encountered, fetches the top 3 tracks based on popularity.
    """
    resolved_tracks = set()
    
    for url in urls:
        try:
            # Clean url to isolate type and ID
            clean_url = url.split('?')[0]
            parts = clean_url.split('/')
            entity_type = parts[-2]
            entity_id = parts[-1]
            
            if entity_type == 'track':
                resolved_tracks.add(entity_id)
                
            elif entity_type == 'album':
                # Pull album tracks and rank by internal popularity
                album_tracks = sp.album_tracks(entity_id)
                track_details = []
                
                # Fetch detailed track objects to inspect popularity metric
                track_ids = [t['id'] for t in album_tracks['items']]
                
                # Spotify allow batching up to 50 tracks for details
                for i in range(0, len(track_ids), 50):
                    batch = sp.tracks(track_ids[i:i+50])
                    track_details.extend(batch['tracks'])
                
                # Sort by popularity descending and grab top 3
                sorted_tracks = sorted(track_details, key=lambda x: x.get('popularity', 0), reverse=True)
                for track in sorted_tracks[:3]:
                    resolved_tracks.add(track['id'])
                    
        except Exception as e:
            print(f"Failed to process Spotify entity {url}: {e}")
            continue
            
    return list(resolved_tracks)


def sync_playlist_state(sp: spotipy.Spotify, playlist_id: str, target_tracks: list[str]) -> dict:
    """
    Compares target track IDs against existing tracks to calculate mutations.
    Enforces the 30-day sliding window rule.
    """
    current_tracks_data = get_current_playlist_tracks(sp, playlist_id)
    current_track_ids = {t['id'] for t in current_tracks_data}
    
    # 1. Identify older tracks to remove (added over 30 days ago)
    now = datetime.now(timezone.utc)
    lookback_limit = now - timedelta(days=30)
    
    tracks_to_remove = []
    for track in current_tracks_data:
        # Spotify returns ISO timestamps: "2026-05-19T10:00:00Z"
        added_date = datetime.fromisoformat(track['added_at'].replace('Z', '+00:00'))
        if added_date < lookback_limit:
            tracks_to_remove.append(track['id'])
            
    # 2. Identify new tracks to add (in targets but not in current playlist)
    tracks_to_add = [t for t in target_tracks if t not in current_track_ids]
    
    # 3. Execute Mutations in batches of 100 (Spotify API restriction)
    if tracks_to_remove:
        for i in range(0, len(tracks_to_remove), 100):
            sp.playlist_remove_specific_occurrences_of_items(playlist_id, [{"uri": t} for t in tracks_to_remove[i:i+100]])
            
    if tracks_to_add:
        for i in range(0, len(tracks_to_add), 100):
            sp.playlist_add_items(playlist_id, tracks_to_add[i:i+100])
            
    return {
        "execution_date": now.isoformat(),
        "tracks_added_count": len(tracks_to_add),
        "tracks_removed_count": len(tracks_to_remove),
        "tracks_added_list": tracks_to_add,
        "tracks_removed_list": tracks_to_remove,
        "total_playlist_size": len(current_track_ids) - len(tracks_to_remove) + len(tracks_to_add)
    }
