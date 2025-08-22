import os
from openai import OpenAI

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key= os.environ["OPENAI_API_KEY"],
)

completion = client.chat.completions.create(
  extra_headers={
},
  extra_body={},
  model="openai/gpt-oss-20b:free",
  messages=[
    {
      "role": "user",
      "content": "How are you when it's raining?"
    }
  ]
)
print(completion.choices[0].message.content)