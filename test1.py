import os
import openai
 
# read api key from environment variable   
# make sure key does not have trailing new line
# if so unset then reset otherwise any api call fail
openai.api_key = os.environ["OPENAI_API_KEY"]

# print(openai.api_key)

client = openai.OpenAI()

response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "user", "content": "Hi"}
    ]
)
print(response.choices[0].message.content)
# input="Write a wish for me for the coming new year 2026"
# print(response.output_text)
