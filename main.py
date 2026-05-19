# main.py
from src.config import AppConfig
from src.reddit_client import fetch_reddit_data
from src.gcs_client import upload_to_gcs
from src.spotify_client import (
    get_spotify_client, 
    extract_spotify_urls, 
    resolve_track_ids, 
    sync_playlist_state
)
from src.bq_client import log_pipeline_results

def run_pipeline():
    print("Starting Spotipunk Data Pipeline...")
    
    # Phase 1: Reddit Extraction & GCS Staging
    raw_reddit_posts = fetch_reddit_data(
        subreddit_name=AppConfig.SUBREDDIT, 
        timeframe="week", 
        limit=50
    )
    
    if not raw_reddit_posts:
        print("No raw data retrieved from Reddit. Exiting run.")
        return
        
    upload_to_gcs(raw_reddit_posts, AppConfig.SUBREDDIT)
    
    # Phase 2: Spotify Link Parsing & Track Resolution
    sp_client = get_spotify_client()
    found_urls = extract_spotify_urls(raw_reddit_posts)
    target_track_ids = resolve_track_ids(sp_client, found_urls)
    
    # Phase 3: Syncing State to Spotify & Logging Mutations to BigQuery
    sync_summary = sync_playlist_state(
        sp=sp_client, 
        playlist_id=AppConfig.SPOTIFY_PLAYLIST_ID, 
        target_tracks=target_track_ids
    )
    
    log_pipeline_results(sync_summary)
    print("Spotipunk Data Pipeline execution completed successfully.")

if __name__ == "__main__":
    run_pipeline()