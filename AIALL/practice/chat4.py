from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

prompt = """
Solve the following problem using Self-Consistency.

Generate 3 independent reasoning paths.
Each path should have:
- Brief reasoning
- Final answer

Finally, compare all answers and output the most consistent answer.

Question:
A train travels 80 km in 1 hour.
How far will it travel in 6 hours?
"""

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt
)

print(response.text)