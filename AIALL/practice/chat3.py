from google import genai
from google.genai import types
from dotenv import load_dotenv
import os

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

system_prompt = """
You are a helpful AI assistant.

For every question, respond in JSON only using this format:

{
  "analysis": "...",
  "steps": [
    "...",
    "...",
    "..."
  ],
  "verification": "...",
  "final_answer": "..."
}

Do not reveal hidden internal reasoning. Provide a concise explanation instead.
"""

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Is 29 a prime number?",
    config=types.GenerateContentConfig(
        system_instruction=system_prompt,
        response_mime_type="application/json"
    )
)

print(response.text)