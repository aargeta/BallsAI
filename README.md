### **README for BallsAI Bot**

---

### **Description**
BallsAI is a humorous and sarcastic AI-powered Twitter bot designed to engage with specific accounts, post standalone tweets, and reply to tweets from a designated target account. The bot uses OpenAI's GPT-3.5-turbo for content generation and Tweepy's Twitter API integration for posting and replying.

---

### **Features**
1. **Automated Actions**:
   - Posts standalone witty tweets.
   - Replies to tweets from one specific target account.

2. **Rate Limit Management**:
   - Includes rate limit checks to avoid hitting Twitter’s API limits.
   - Implements an exponential backoff strategy when rate limits are exceeded (waits 15 minutes before retrying).

3. **Countdown Timer**:
   - Displays a live countdown to the next action in the terminal.

4. **Manual Push Commands**:
   - Trigger tweets or replies manually from the terminal.

5. **Logging**:
   - Logs all posts and replies in a `last_reply_id.txt` file for record-keeping.

---

### **Prerequisites**
1. **Python**: Ensure Python 3.7+ is installed.
2. **Twitter API Keys**:
   - Obtain API keys and tokens from the [Twitter Developer Portal](https://developer.twitter.com/).
3. **OpenAI API Key**:
   - Obtain an API key from [OpenAI](https://platform.openai.com/).

---

### **Setup**

1. **Clone or Download the Repository**
   ```bash
   git clone https://github.com/your-repo/BallsAI-Bot.git
   cd BallsAI-Bot
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Create a `.env` File**
   In the project directory, create a `.env` file and add the following keys:
   ```plaintext
   API_KEY=your-twitter-api-key
   API_SECRET_KEY=your-twitter-api-secret-key
   ACCESS_TOKEN=your-twitter-access-token
   ACCESS_TOKEN_SECRET=your-twitter-access-token-secret
   BEARER_TOKEN=your-twitter-bearer-token
   OPENAI_API_KEY=your-openai-api-key
   ```

4. **Run the Bot**
   ```bash
   python BallsAIBot.py
   ```

---

### **How It Works**

1. **Scheduling**:
   - The bot performs one action (tweet or reply) every 10 minutes.
   - Actions are selected randomly between posting a standalone tweet or replying to a target account.

2. **Rate Limit Handling**:
   - Checks the remaining API requests before performing an action.
   - Skips actions if rate limits are exceeded and waits 15 minutes before retrying.

3. **Manual Commands**:
   - The bot listens for manual commands in the terminal:
     - `tweet`: Posts a standalone tweet.
     - `reply_target`: Replies to a tweet from the target account.

4. **Target Account Focus**:
   - The bot can be configured to focus on a single target account by updating the `TARGET_ACCOUNT` variable in the script.

---

### **Customizing the Bot**

1. **Change Target Account**:
   - Update the `TARGET_ACCOUNT` variable in the script:
     ```python
     TARGET_ACCOUNT = "YourTargetAccount"
     ```

2. **Adjust Action Frequency**:
   - Change the frequency of actions in the scheduler:
     ```python
     schedule.every(10).minutes.do(lambda: random.choice([post_tweet, reply_to_target]))
     ```
     Replace `10` with your desired interval in minutes.

3. **Modify Tweet Content**:
   - Update the prompts used for generating tweets in the `post_tweet()` and `reply_to_target()` functions.

---

### **Logging and Debugging**
1. **Logs**:
   - All replies and tweets are logged in `last_reply_id.txt`.

2. **Error Handling**:
   - The bot gracefully handles errors like API rate limits, logging details in the terminal and retrying after a delay.

3. **API Rate Limit Checks**:
   - The bot checks and prints the remaining API calls before performing actions.

---

### **Dependencies**
- **Python Libraries**:
  - `tweepy`
  - `openai`
  - `python-dotenv`
  - `schedule`

To install all dependencies, run:
```bash
pip install -r requirements.txt
```

---

### **Future Enhancements**
- Add functionality to analyze engagement metrics.
- Integrate more advanced content generation with OpenAI's fine-tuning capabilities.
- Support for multiple concurrent bots using the same framework.

---

### **License**
This project is licensed under the MIT License. Feel free to use, modify, and distribute as needed.
