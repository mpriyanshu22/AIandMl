import os
os.environ["MEM0_TELEMETRY"] = "False"

from dotenv import load_dotenv
from google import genai
from google.genai import types
from mem0 import Memory

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
NEO4J_URL = os.getenv("NEO4J_URL", "bolt://localhost:7687")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "")

# Unified Mem0 Config with Graph Store enabled
config = {
    "version": "v1.1",
    "embedder": {
        "provider": "gemini",
        "config": {
            "api_key": GEMINI_API_KEY,
            "model": "models/gemini-embedding-001",
        },
    },
    "llm": {
        "provider": "gemini",
        "config": {
            "api_key": GEMINI_API_KEY,
            "model": "gemini-3.1-flash-lite",
        },
    },
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "host": QDRANT_HOST,
            "port": 6333,
            "collection_name": "mem0_gemini",
            "embedding_model_dims": 768,
        },
    },
    "graph_store": {
        "provider": "neo4j",
        "config": {
            "url": NEO4J_URL,
            "username": NEO4J_USERNAME,
            "password": NEO4J_PASSWORD,
            "database": "neo4j",
        },
    },
}

# Initialize Mem0 client
memory_client = Memory.from_config(config)
client = genai.Client(api_key=GEMINI_API_KEY)


def chat(message: str, user_id: str = "default_user") -> str:
    # 1. Search existing memories (Vector + Graph)
    relevant_memories = memory_client.search(
        query=message,
        filters={"user_id": user_id},
    )

    context_str = ""
    if relevant_memories and "results" in relevant_memories:
        context_str = "\n".join([m["memory"] for m in relevant_memories["results"]])

    system_instruction = (
        f"You are a helpful assistant. Use these relevant memories if applicable:\n{context_str}"
        if context_str
        else "You are a helpful assistant."
    )

    # 2. Call Gemini
    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=message,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
        ),
    )

    # 3. Store conversation in both Vector and Neo4j Graph
    memory_client.add(
        f"User: {message}\nAssistant: {response.text}",
        user_id=user_id,
    )

    return response.text


if __name__ == "__main__":
    while True:
        try:
            user_input = input(">> ")
            if user_input.strip().lower() in ["exit", "quit"]:
                break
            print("BOT:", chat(message=user_input))
        except KeyboardInterrupt:
            break