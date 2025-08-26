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
# Global model config
# ----------------------------
MODEL_NAME = "qwen/qwen3-coder:free"

# ----------------------------
# Retry wrapper for API calls
# ----------------------------
@retry_request(retries=5, backoff_factor=2)
def get_completion(prompt: str) -> str:
    """Return the full completion text (non-streaming)."""
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content  # ✅ return plain text

@retry_request(retries=5, backoff_factor=2)
def get_reply(prompt: str):
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            stream=True
        )
        for chunk in response:
            if chunk.choices[0].delta.content:  # check before printing
                yield chunk.choices[0].delta.content
    except (InternalServerError, RateLimitError) as err:
        yield f'error occurred\n{err}'

# ----------------------------
# Main
# ----------------------------
if __name__ == "__main__":
    # Example: streaming reply
    # for reply in get_reply("please introduce Taipei"):
    #     print(reply, end='')

    # Example: single completion
    completion = get_completion("Hello, how are you?")
    pprint(completion)
