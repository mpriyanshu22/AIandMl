# from dotenv import load_dotenv
# from openai import OpenAI

# load_dotenv()

# client = OpenAI()

# result = client.chat.completions.create(
#     model="gpt-4",
#     messages=[
#         { "role": "user", "content": "What is greator? 9.8 or 9.11" } # Zero Shot Prompting
#     ]
# )

# print(result.choices[0].message.content)
from google import genai
from dotenv import load_dotenv
import os
from google.genai import types

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

response = client.models.generate_content(
    model='gemini-2.5-flash', contents='Why is the sky blue?'
)
print(response.text)