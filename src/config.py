# src/config.py
import os
from dotenv import load_dotenv

# Load local .env file if running locally; Cloud Run will use actual env vars
load_dotenv()

class AppConfig:
    # GCP Environment Infrastructure
    GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
    RAW_VAULT_BUCKET = os.getenv("RAW_VAULT_BUCKET", "spotipunk-raw-vault")
    SUBREDDIT = os.getenv("SUBREDDIT", "poppunkers")

    # API Credentials (Injected securely by GCP Secret Manager)
    REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
    REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")
    REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT")
    
    SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
    SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
    SPOTIFY_PLAYLIST_ID = os.getenv("SPOTIFY_PLAYLIST_ID")
    SPOTIFY_REFRESH_TOKEN = os.getenv("SPOTIFY_REFRESH_TOKEN")
