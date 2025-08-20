import os
import openai
 
openai.api_key = os.environ["OPENAI_API_KEY"]

print(openai.api_key)