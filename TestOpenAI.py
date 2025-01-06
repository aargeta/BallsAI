from dotenv import load_dotenv
import os
import openai

# Load the .env file
load_dotenv()

# Set the API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Test the API
try:
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # Or 'gpt-4' if enabled for your project
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Test the API with sk-proj key."},
        ]
    )
    print("API is working!")
    print("Response:", response["choices"][0]["message"]["content"])
except openai.error.AuthenticationError:
    print("Authentication failed. Check your API key or project settings.")
except openai.error.OpenAIError as e:
    print(f"An error occurred: {e}")

