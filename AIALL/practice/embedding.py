from dotenv import load_dotenv
import os
from google import genai

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

response = client.models.embed_content(
    model="gemini-embedding-001",
    contents = [
    "I love cricket",
    "Python is a programming language",
    "The weather is nice today"
]
)

print(len(response.embeddings[0].values))
print(response.embeddings[0].values)