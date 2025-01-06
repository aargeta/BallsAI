import tweepy
import schedule
import time
from datetime import datetime, timedelta
import threading
import os
import random  # Ensure random is imported
from dotenv import load_dotenv
import logging
import openai

# Load API keys from .env
load_dotenv()

API_KEY = os.getenv('API_KEY')
API_SECRET_KEY = os.getenv('API_SECRET_KEY')
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
ACCESS_TOKEN_SECRET = os.getenv('ACCESS_TOKEN_SECRET')
BEARER_TOKEN = os.getenv('BEARER_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Set OpenAI API key
openai.api_key = OPENAI_API_KEY

# Tweepy Client for v2 endpoints
client = tweepy.Client(
    bearer_token=BEARER_TOKEN,
    consumer_key=API_KEY,
    consumer_secret=API_SECRET_KEY,
    access_token=ACCESS_TOKEN,
    access_token_secret=ACCESS_TOKEN_SECRET,
)

# Logging setup
logging.basicConfig(filename="bot_log.txt", level=logging.INFO)

# Target account
TARGET_ACCOUNT = "0xpenais"  # Only focus on this account
last_replied_id = None  # Track last replied tweet ID

# Timer tracking
next_action_time = None  # To track when the next action will occur
last_reply_log_file = "last_reply_id.txt"  # File to log last post details


# Function to log last post details
def log_last_post(time, account, content):
    try:
        with open(last_reply_log_file, "a", encoding="utf-8") as file:
            file.write(f"Time: {time}, Account: {account}, Content: {content}\n")
        print(f"Logged last post: Time: {time}, Account: {account}, Content: {content}")
    except Exception as e:
        print(f"Failed to log post: {e}")
        logging.error(f"Failed to log post: {e}")


# Function to generate AI content using OpenAI
def generate_ai_content(prompt, max_tokens=50):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a humorous and sarcastic AI bot named BallsAI. Be witty and engaging."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=max_tokens,
            temperature=0.7
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"Error generating content: {e}")
        return "BallsAI is having a brain fart. 🥜💨"


# Function to check API rate limits
def check_rate_limit():
    try:
        response = client.get_user(username="TwitterDev")  # Lightweight endpoint to test limits
        remaining = int(response.headers.get("x-rate-limit-remaining", 0))
        reset_time = datetime.fromtimestamp(int(response.headers.get("x-rate-limit-reset", time.time())))
        print(f"Rate limit remaining: {remaining}, resets at: {reset_time}")
        return remaining, reset_time
    except Exception as e:
        print(f"Error checking rate limit: {e}")
        return 0, datetime.now() + timedelta(minutes=15)  # Default to a 15-minute wait if an error occurs


# Function to reply to the target account
def reply_to_target():
    global next_action_time, last_replied_id
    try:
        print(f"Focusing on target account: @{TARGET_ACCOUNT}")
        remaining, reset_time = check_rate_limit()
        if remaining == 0:
            print(f"Rate limit reached. Skipping reply to @{TARGET_ACCOUNT}.")
            return

        response = client.get_users_tweets(
            id=client.get_user(username=TARGET_ACCOUNT).data.id,
            max_results=5
        )
        tweets = response.data
        if not tweets:
            print(f"No tweets found for account: @{TARGET_ACCOUNT}")
            return

        latest_tweet = tweets[0]
        if last_replied_id == latest_tweet.id:
            print(f"Already replied to the latest tweet from @{TARGET_ACCOUNT}. Skipping.")
            return

        # Generate AI reply
        prompt = f"Write a witty reply to this tweet as a self-aware blockchain ballsack:\n\n{latest_tweet.text}"
        reply_content = generate_ai_content(prompt, max_tokens=75)

        # Reply to the tweet
        client.create_tweet(text=f"@{TARGET_ACCOUNT} {reply_content}", in_reply_to_tweet_id=latest_tweet.id)
        print(f"Replied to @{TARGET_ACCOUNT}'s tweet: {reply_content}")
        log_last_post(datetime.now(), TARGET_ACCOUNT, reply_content)
        last_replied_id = latest_tweet.id
        next_action_time = datetime.now() + timedelta(minutes=10)
    except tweepy.errors.TooManyRequests:
        print(f"Rate limit exceeded while replying to @{TARGET_ACCOUNT}. Retrying after 15 minutes...")
        time.sleep(900)  # Wait for 15 minutes before retrying
    except tweepy.errors.TweepyException as e:
        print(f"Failed to reply to @{TARGET_ACCOUNT}: {e}")


# Function to post a standalone AI-generated tweet
def post_tweet():
    global next_action_time
    try:
        remaining, reset_time = check_rate_limit()
        if remaining == 0:
            print("Rate limit reached. Skipping tweet.")
            return

        prompt = "Write a funny and witty tweet about blockchain as if you are a self-aware ballsack."
        tweet = generate_ai_content(prompt)

        response = client.create_tweet(text=tweet)
        print(f"Posted tweet at {datetime.now()}: {tweet}")
        log_last_post(datetime.now(), "Standalone Tweet", tweet)
        next_action_time = datetime.now() + timedelta(minutes=10)
    except tweepy.errors.TooManyRequests:
        print("Rate limit exceeded while posting a tweet. Retrying after 15 minutes...")
        time.sleep(900)  # Wait for 15 minutes before retrying
    except tweepy.errors.TweepyException as e:
        print(f"Failed to post tweet: {e}")


# Timer thread to display countdown
def countdown_timer():
    while True:
        if next_action_time:
            remaining_time = next_action_time - datetime.now()
            if remaining_time.total_seconds() > 0:
                print(f"Next action in: {str(remaining_time).split('.')[0]}", end="\r")
            else:
                print("Next action is about to run!", end="\r")
        time.sleep(1)


# Command prompt listener for manual push
def command_prompt_listener():
    global next_action_time
    while True:
        command = input("\nEnter a command (tweet, reply_target): ").strip().lower()
        if command == "tweet":
            post_tweet()
        elif command == "reply_target":
            reply_to_target()
        else:
            print("Invalid command. Try 'tweet' or 'reply_target'.")
        next_action_time = datetime.now() + timedelta(minutes=10)


# Scheduler: Every 10 minutes
schedule.every(10).minutes.do(lambda: random.choice([post_tweet, reply_to_target]))

if __name__ == "__main__":
    next_action_time = datetime.now() + timedelta(minutes=10)
    threading.Thread(target=countdown_timer, daemon=True).start()
    threading.Thread(target=command_prompt_listener, daemon=True).start()
    print("BallsAI Bot is running...")
    while True:
        schedule.run_pending()
        time.sleep(1)
