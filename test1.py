import os
import openai
 
# read api key from environment variable   
# make sure key does not have trailing new line
# if so unset then reset otherwise any api call fail
openai.api_key = os.environ["OPENAI_API_KEY"]

print(openai.api_key)

from openai import OpenAI

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=openai.api_key,
)

completion = client.chat.completions.create(
  extra_headers={},
  extra_body={},
  model="openai/gpt-oss-20b:free",
  messages=[
    {
      "role": "user",
      "content": "What is the meaning of life?"
    }
  ]
)
print(completion.choices[0].message.content)