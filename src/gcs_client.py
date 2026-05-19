import json
from datetime import datetime
from google.cloud import storage
from src.config import AppConfig

def upload_to_gcs(data: list[dict], subreddit: str):
    """
    Serializes data and saves it to GCS.
    Path: gs://[BUCKET]/[SUBREDDIT]/[YYYY-MM-DD]/[TIMESTAMP].json
    """
    # Initialize client
    client = storage.Client(project=AppConfig.GCP_PROJECT_ID)
    bucket = client.bucket(AppConfig.RAW_VAULT_BUCKET)
    
    # Generate path
    now = datetime.utcnow()
    date_str = now.strftime("%Y-%m-%d")
    timestamp = now.strftime("%H%M%S")
    blob_path = f"{subreddit}/{date_str}/run_{timestamp}.json"
    
    # Serialize and Upload
    blob = bucket.blob(blob_path)
    json_data = json.dumps(data, indent=2)
    
    blob.upload_from_string(
        data=json_data,
        content_type='application/json'
    )
    
    print(f"Successfully uploaded {len(data)} posts to gs://{AppConfig.RAW_VAULT_BUCKET}/{blob_path}")
    return blob_path