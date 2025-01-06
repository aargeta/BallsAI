import tweepy
import schedule
import time
from datetime import datetime, timedelta
import threading
import os
import random
from urllib.parse import urlparse  # For extracting username from URL
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

# URL of the target account
TARGET_ACCOUNT_URL = "https://x.com/0xpenais"  # Replace with the desired account URL

# Function to extract username from a URL
def extract_username_from_url(url):
    try:
        parsed_url = urlparse(url)
        username = parsed_url.path.strip("/")
        if not username:
            raise ValueError("No username found in the URL.")
        print(f"Extracted username: {username}")
        return username
    except Exception as e:
        print(f"Error extracting username from URL: {e}")
        return None

# Extract username dynamically from URL
TARGET_ACCOUNT = extract_username_from_url(TARGET_ACCOUNT_URL)
if not TARGET_ACCOUNT:
    print("Error: Unable to extract username. Please check the URL.")
    exit(1)

print(f"Target account set to: {TARGET_ACCOUNT}")

# Timer tracking
next_action_time = None  # To track when the next action will occur
last_replied_id = None  # Track last replied tweet ID
last_reply_log_file = "last_reply_id.txt"  # File to log last post details

# Function to clear console lines
def clear_console_line():
    """
    Clears the current console line.
    """
    print("\r" + " " * 80, end="\r")

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
        user = client.get_user(username=TARGET_ACCOUNT)
        if user.data is None:
            print("Error: User not found or invalid username provided.")
            return 0, datetime.now() + timedelta(minutes=15)

        response = client.get_users_tweets(id=user.data.id, max_results=5)
        rate_limit_remaining = response.meta.get("x-rate-limit-remaining", 0)
        rate_limit_reset = datetime.fromtimestamp(int(response.meta.get("x-rate-limit-reset", time.time())))
        print(f"Rate limit remaining: {rate_limit_remaining}, resets at: {rate_limit_reset}")
        return rate_limit_remaining, rate_limit_reset
    except tweepy.errors.TooManyRequests:
        print("Rate limit exceeded.")
        return 0, datetime.now() + timedelta(minutes=15)
    except Exception as e:
        print(f"Error checking rate limit: {e}")
        return 0, datetime.now() + timedelta(minutes=15)

# Function to display rate limit status
def display_rate_limit_status():
    """
    Display the rate limit status by calling the `check_rate_limit` function.
    """
    try:
        remaining, reset_time = check_rate_limit()
        if remaining == 0:
            print(f"Rate limit reached. Next action available after: {reset_time}")
        else:
            print(f"Rate limit remaining: {remaining}. Next reset at: {reset_time}")
    except Exception as e:
        print(f"Error retrieving rate limit status: {e}")

# Function to reply to the target account
def reply_to_target():
    global next_action_time, last_replied_id
    try:
        print(f"Focusing on target account: @{TARGET_ACCOUNT}")
        
        # Get the user data
        user = client.get_user(username=TARGET_ACCOUNT)
        if not user or not user.data:
            print(f"Error: User '{TARGET_ACCOUNT}' not found or invalid username provided.")
            return

        # Fetch tweets for the user
        response = client.get_users_tweets(id=user.data.id, max_results=5)
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
    except tweepy.errors.NotFound:
        print(f"Error: The user '{TARGET_ACCOUNT}' does not exist.")
    except tweepy.errors.TooManyRequests:
        print(f"Rate limit exceeded while replying to @{TARGET_ACCOUNT}. Retrying after 15 minutes...")
        time.sleep(900)  # Wait for 15 minutes before retrying
    except Exception as e:
        print(f"Failed to reply to @{TARGET_ACCOUNT}: {e}")

# Function to post a standalone AI-generated tweet
def post_tweet():
    global next_action_time
    try:
        remaining, reset_time = check_rate_limit()
        if remaining == 0:
            print(f"Rate limit reached. Next tweet available after: {reset_time}")
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
    last_displayed_time = None  # Track the last displayed time
    while True:
        if next_action_time:
            remaining_time = next_action_time - datetime.now()
            if remaining_time.total_seconds() > 0:
                remaining_time_str = f"Next action in: {str(remaining_time).split('.')[0]}"
                if remaining_time_str != last_displayed_time:
                    clear_console_line()  # Clear the current line before printing the timer
                    print(f"{remaining_time_str} ", end="", flush=True)
                    last_displayed_time = remaining_time_str
            else:
                clear_console_line()
                print("Next action is about to run!              ", end="", flush=True)
                last_displayed_time = "Next action is about to run!"
        time.sleep(1)

# Command prompt listener for manual push
def command_prompt_listener():
    global next_action_time
    while True:
        print("\nEnter a command (tweet, reply_target, check_rate): ", end="", flush=True)
        command = input().strip().lower()
        clear_console_line()  # Clear the input prompt line after receiving input
        if command == "tweet":
            clear_console_line()  # Ensure clean output before action
            post_tweet()
        elif command == "reply_target":
            clear_console_line()  # Ensure clean output before action
            reply_to_target()
        elif command == "check_rate":
            clear_console_line()  # Ensure clean output before displaying rate limit
            display_rate_limit_status()
        else:
            print("\nInvalid command. Try 'tweet', 'reply_target', or 'check_rate'.")

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
