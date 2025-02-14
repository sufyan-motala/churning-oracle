import praw
from datetime import datetime
from app.config import config


class RedditScraper:
    def __init__(self):
        print("Initializing Reddit API connection...")
        self.reddit = praw.Reddit(
            client_id=config.REDDIT_CLIENT_ID,
            client_secret=config.REDDIT_CLIENT_SECRET,
            user_agent="churning-oracle",
        )
        self.subreddit = self.reddit.subreddit("churningcanada")
        print("Reddit API connection established")

    def get_daily_threads(self, days_back=5):
        """Fetch daily question threads from the last n days"""
        print(f"Fetching {days_back} days of daily threads...")
        posts = []
        for submission in self.subreddit.search(
            'title:"Daily Question Thread"', sort="new", limit=days_back
        ):
            print(
                f"Processing thread from {datetime.fromtimestamp(submission.created_utc).strftime('%Y-%m-%d')}"
            )
            posts.append(self._process_submission(submission))
        print(f"Fetched {len(posts)} daily threads")
        return posts

    def _process_submission(self, submission):
        """Process a submission and its comments"""
        submission_data = {
            "id": submission.id,
            "title": submission.title,
            "date": datetime.fromtimestamp(submission.created_utc).strftime("%Y-%m-%d"),
            "comments": [],
        }

        print(f"Loading comments for thread {submission.id}...")
        submission.comments.replace_more(limit=None)  # Load all comments
        for comment in submission.comments.list():
            comment_data = {
                "id": comment.id,
                "body": comment.body,
                "score": comment.score,
                "parent_id": comment.parent_id,
                "created_utc": comment.created_utc,
            }
            submission_data["comments"].append(comment_data)

        print(f"Processed {len(submission_data['comments'])} comments")
        return submission_data
