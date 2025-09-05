import os
import tweepy
import feedparser
import random
import time
import logging

# ===============================
# 0. Setup Logging
# ===============================
logging.basicConfig(
    filename="bot.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
console.setFormatter(formatter)
logging.getLogger("").addHandler(console)

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
# 2. Track Posted Headlines in File
# ===============================
POSTED_FILE = "posted.txt"

def load_posted_titles():
    if not os.path.exists(POSTED_FILE):
        return set()
    with open(POSTED_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f.readlines())

def save_posted_title(title):
    with open(POSTED_FILE, "a", encoding="utf-8") as f:
        f.write(title + "\n")

posted_titles = load_posted_titles()

# ===============================
# 3. Auto-Post from Multiple Sports RSS Feeds
# ===============================
RSS_FEEDS = [
    "https://www.espn.com/espn/rss/news",
    "https://www.espn.com/espn/rss/nfl/news",
    "https://www.espn.com/espn/rss/mlb/news",
    "https://www.espn.com/espn/rss/nba/news"
]

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
                save_posted_title(title)
                logging.info(f"Tweeted: {tweet}")
                return  # only post 1 item per cycle
            except Exception as e:
                logging.error(f"Error posting: {e}")
    logging.info("No new items to post.")

# ===============================
# 4. Auto-Reply / Like / Retweet
# ===============================
SEARCH_TERMS = ["NFL", "NBA", "Yankees", "Touchdown", "Goal"]
REPLIES = [
    "🔥 What a play!",
    "👀 Did you catch that?",
    "👏 Pure hustle right there.",
    "💯 Facts!",
    "🏆 Championship vibes."
]

def engage_with_tweets():
    for tweet in tweepy.Cursor(api.search_tweets, q=" OR ".join(SEARCH_TERMS), lang="en").items(3):
        try:
            if not tweet.favorited:
                # Randomly choose action
                action = random.choice(["reply", "like", "retweet"])

                if action == "reply":
                    message = random.choice(REPLIES)
                    api.update_status(
                        status=message,
                        in_reply_to_status_id=tweet.id,
                        auto_populate_reply_metadata=True
                    )
                    api.create_favorite(tweet.id)
                    logging.info(f"Replied to @{tweet.user.screen_name}: {message}")

                elif action == "like":
                    api.create_favorite(tweet.id)
                    logging.info(f"Liked tweet from @{tweet.user.screen_name}")

                elif action == "retweet":
                    api.retweet(tweet.id)
                    logging.info(f"Retweeted @{tweet.user.screen_name}")

                time.sleep(random.randint(15, 40))  # pause between actions
        except Exception as e:
            logging.error(f"Error engaging: {e}")

# ===============================
# 5. Main Bot Loop (Random Delay)
# ===============================
while True:
    post_from_rss()
    engage_with_tweets()

    delay = random.randint(1500, 2700)  # 25–45 minutes
    logging.info(f"Sleeping for {delay//60} minutes...")
    time.sleep(delay)
