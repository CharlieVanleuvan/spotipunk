import praw
import re
from reddit_creds import client_id,client_secret,user_agent

def reddit_client(subreddit: str,
                  period: str,
                  client_id: str,
                  client_secret: str,
                  user_agent: str) -> list:
    """
    Authenticate with Reddit and pull the top posts from the period specified
    Can be hour, day, week, month, year, all
    """
    reddit = praw.Reddit(client_id=client_id,client_secret=client_secret,user_agent = user_agent)
    top_posts = reddit.subreddit(subreddit).top(time_filter = period)
    album_tags = {'album_tag':[],'post_title':[],'post_comment':[]}
    track_tags = {'track_tag':[],'post_title':[],'post_comment':[]}
    for post in top_posts:
        title_link_match = re.search(r'(?<=open\.spotify\.com\/album/)[\d\w]+|(?<=open\.spotify\.com\/track/)[\d\w]+',post.url)
        is_album = True if re.search(r'(?<=open\.spotify\.com\/album/)[\d\w]+',post.url) else False
        if title_link_match:
            spotify_tag_id = title_link_match.group()
            if is_album:
                #add this tag to collection
                album_tags['album_tag'].append(spotify_tag_id)
                album_tags['post_title'].append(post.title)
                album_tags['post_comment'].append(None)
            else:
                track_tags['track_tag'].append(spotify_tag_id)
                track_tags['post_title'].append(post.title)
                track_tags['post_comment'].append(None)
        
        #now check all comments
        submission = reddit.submission(id = post.id)
        submission.comments.replace_more() #need to call this to flatten out the comment trees
        for comment in submission.comments.list():
            comment_link_match = re.search(r'(?<=open\.spotify\.com\/album/)[\d\w]+|(?<=open\.spotify\.com\/track/)[\d\w]+',comment.body)
            is_album = True if re.search(r'(?<=open\.spotify\.com\/album/)[\d\w]+',comment.body) else False
            if comment_link_match:
                spotify_tag_id = comment_link_match.group()
                if is_album:
                    album_tags['album_tag'].append(spotify_tag_id)
                    album_tags['post_title'].append(comment.body)
                    album_tags['post_comment'].append(None)
                else:
                    track_tags['track_tag'].append(spotify_tag_id)
                    track_tags['post_title'].append(comment.body)
                    track_tags['post_comment'].append(None) 

    return [album_tags,track_tags]