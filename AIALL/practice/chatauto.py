import json
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

# Initialize the Gemini Client
# It automatically picks up GEMINI_API_KEY from your environment
client = genai.Client()

system_prompt = """
You are an AI assistant who is expert in breaking down complex problems and then resolve the user query.

For the given user input, analyse the input and break down the problem step by step.
Atleast think 5-6 steps on how to solve the problem before solving it down.

The steps are you get a user input, you analyse, you think, you again think for several times and then return an output with explanation and then finally you validate the output as well before giving final result.

Follow the steps in sequence that is "analyse", "think", "output", "validate" and finally "result".

Rules:
1. Follow the strict JSON output as per Output schema.
2. Always perform one step at a time and wait for next input
3. Carefully analyse the user query

Output Format (Strict JSON):
{ "step": "string", "content": "string" }
"""

# Configure the model settings
config = types.GenerateContentConfig(
    system_instruction=system_prompt,
    response_mime_type="application/json", # Forces JSON output
    temperature=0.7
)

# Start a multi-turn chat session
chat = client.chats.create(
    model="gemini-3.1-flash-lite",
    config=config
)

# Get the initial query from the user
query = input("> ")

# Send the initial query to kickstart the chain
response = chat.send_message(query)

while True:
    try:
        # Parse the JSON response text
        parsed_response = json.loads(response.text)
    except json.JSONDecodeError:
        print("🤖 Failed to parse JSON configuration from model.")
        break

    step = parsed_response.get("step")
    content = parsed_response.get("content")

    # Print the thinking/analysis or the result based on the step
    if step != "output":
        print(f"🧠 [{step.upper()}]: {content}")
    else:
        print(f"🤖 [OUTPUT]: {content}")
        break  # Exit the loop once the final output step is reached

    # Prompt the model to generate the NEXT step in the sequence
    # Because we are using the 'chat' object, Gemini remembers the previous step it just generated
    response = chat.send_message("Generate the next step only.")