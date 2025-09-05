import os
import tweepy
import feedparser
import random
import time

# ===============================
# 1. Authenticate with ENV VARS
# ===============================
API_KEY = os.environ["API_KEY"]
API_SECRET = os.environ["API_SECRET"]
ACCESS_TOKEN = os.environ["ACCESS_TOKEN"]
ACCESS_SECRET = os.environ["ACCESS_SECRET"]

auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET)
api = tweepy.API(auth)

# ===============================
# 2. Auto-Post from Multiple Sports RSS Feeds
# ===============================
RSS_FEEDS = [
    "https://www.espn.com/espn/rss/news",
    "https://www.espn.com/espn/rss/nfl/news",
    "https://www.espn.com/espn/rss/mlb/news",
    "https://www.espn.com/espn/rss/nba/news"
]

# keep track of already-posted headlines
posted_titles = set()

def post_from_rss():
    global posted_titles
    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)
        if not feed.entries:
            continue

        latest = feed.entries[0]
        title = latest.title
        link = latest.link

        if title not in posted_titles:
            tweet = f"🏆 {title}\n{link}"
            try:
                api.update_status(tweet)
                posted_titles.add(title)
                print("Tweeted:", tweet)
                return  # only post 1 item per cycle
            except Exception as e:
                print("Error posting:", e)
    print("No new items to post.")

# ===============================
# 3. Auto-Reply to Sports Tweets
# ===============================
SEARCH_TERMS = ["NFL", "NBA", "Yankees", "Touchdown", "Goal"]
REPLIES = [
    "🔥 What a play!",
    "👀 Did you catch that?",
    "👏 Pure hustle right there.",
    "💯 Facts!",
    "🏆 Championship vibes."
]

def auto_reply():
    for tweet in tweepy.Cursor(api.search_tweets, q=" OR ".join(SEARCH_TERMS), lang="en").items(3):
        try:
            if not tweet.favorited:  # avoid repeating the same reply
                message = random.choice(REPLIES)
                api.update_status(
                    status=message,
                    in_reply_to_status_id=tweet.id,
                    auto_populate_reply_metadata=True
                )
                api.create_favorite(tweet.id)  # mark as replied
                print(f"Replied to @{tweet.user.screen_name}: {message}")
                time.sleep(20)
        except Exception as e:
            print("Error replying:", e)

# ===============================
# 4. Main Bot Loop
# ===============================
while True:
    post_from_rss()
    auto_reply()
    time.sleep(1800)  # run every 30 minutes
