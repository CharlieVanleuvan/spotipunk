import praw
from src.config import AppConfig

def get_reddit_session():
    """Initializes the PRAW Reddit instance."""
    return praw.Reddit(
        client_id=AppConfig.REDDIT_CLIENT_ID,
        client_secret=AppConfig.REDDIT_CLIENT_SECRET,
        user_agent=AppConfig.REDDIT_USER_AGENT,
    )

def fetch_reddit_data(subreddit_name: str, timeframe: str = "week", limit: int = 50):
    """
    Extracts raw post and comment data from Reddit.
    Returns a list of dictionaries ready for storage in GCS.
    """
    reddit = get_reddit_session()
    subreddit = reddit.subreddit(subreddit_name)
    
    # Fetch top posts based on the timeframe
    top_posts = subreddit.top(time_filter=timeframe, limit=limit)
    
    extracted_data = []
    
    for post in top_posts:
        # Create a clean dictionary representation of the post
        post_data = {
            "id": post.id,
            "title": post.title,
            "url": post.url,
            "score": post.score,
            "created_utc": post.created_utc,
            "comments": []
        }
        
        # Extract comment text to look for links later
        post.comments.replace_more(limit=0)  # Expand comment tree
        for comment in post.comments.list():
            post_data["comments"].append({
                "id": comment.id,
                "body": comment.body,
                "score": comment.score
            })
            
        extracted_data.append(post_data)
        
    return extracted_data