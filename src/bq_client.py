import uuid
from datetime import datetime, timezone
from google.cloud import bigquery
from src.config import AppConfig

def log_pipeline_results(sync_summary: dict) -> None:
    """
    Streams pipeline execution summaries and track mutations 
    directly into BigQuery tables.
    """
    # Initialize the BigQuery Client
    client = bigquery.Client(project=AppConfig.GCP_PROJECT_ID)
    
    # Generate an explicit run ID to link both tables
    run_id = str(uuid.uuid4())
    now_iso = datetime.now(timezone.utc).isoformat()
    
    dataset_ref = f"{AppConfig.GCP_PROJECT_ID}.playlist_data"
    
    # 1. Prepare Run Metadata Row
    run_rows_to_insert = [{
        "run_id": run_id,
        "execution_timestamp": now_iso,
        "tracks_added_count": sync_summary["tracks_added_count"],
        "tracks_removed_count": sync_summary["tracks_removed_count"],
        "total_playlist_size": sync_summary["total_playlist_size"],
        "status": "SUCCESS"
    }]
    
    # 2. Prepare Ledger Delta Rows
    changelog_rows_to_insert = []
    
    for track_id in sync_summary.get("tracks_added_list", []):
        changelog_rows_to_insert.append({
            "event_timestamp": now_iso,
            "run_id": run_id,
            "track_id": track_id,
            "action": "ADDED"
        })
        
    for track_id in sync_summary.get("tracks_removed_list", []):
        changelog_rows_to_insert.append({
            "event_timestamp": now_iso,
            "run_id": run_id,
            "track_id": track_id,
            "action": "REMOVED"
        })

    # 3. Stream data into BigQuery (Using Insert_Rows for real-time streaming)
    try:
        if run_rows_to_insert:
            run_table = f"{dataset_ref}.pipeline_runs"
            errors = client.insert_rows_json(run_table, run_rows_to_insert)
            if errors: raise RuntimeWarning(f"BQ Run Table Error: {errors}")
            
        if changelog_rows_to_insert:
            changelog_table = f"{dataset_ref}.playlist_changelog"
            errors = client.insert_rows_json(changelog_table, changelog_rows_to_insert)
            if errors: raise RuntimeWarning(f"BQ Changelog Table Error: {errors}")
            
        print(f"Successfully logged execution state ({run_id}) to BigQuery.")
        
    except Exception as e:
        print(f"Failed to log data to BigQuery: {e}")
        # future work --> add alerting
