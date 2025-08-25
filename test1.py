import os
from openai import OpenAI, InternalServerError, RateLimitError
from rich import print as pprint
from retry_decorator import retry_request  # import the decorator
import time

# ----------------------------
# Check API key before anything
# ----------------------------
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    raise ValueError("Please set OPENAI_API_KEY in your environment")

# ----------------------------
# Initialize OpenAI client
# ----------------------------
client = OpenAI(
    base_url="https://openrouter.ai/api/v1"
)

# ----------------------------
# Retry wrapper for API calls
# ----------------------------
@retry_request(retries=5, backoff_factor=2)
def get_completion(prompt: str):
    return client.chat.completions.create(
        model="qwen/qwen3-coder:free",
        messages=[{"role": "user", "content": prompt}],
    )

# ----------------------------
# Main
# ----------------------------
if __name__ == "__main__":
    completion = get_completion("Hello, how are you?")
    # Print only the message content, not the whole object
    pprint(completion)
