# import os
# from dotenv import load_dotenv

# from google import genai
# from langfuse import get_client
# from openinference.instrumentation.google_genai import GoogleGenAIInstrumentor

# load_dotenv()


# def main():

#     # Initialize Langfuse
#     langfuse = get_client()

#     # Enable automatic tracing for Google GenAI
#     GoogleGenAIInstrumentor().instrument()

#     # Gemini client
#     gemini_client = genai.Client(
#         api_key=os.getenv("GEMINI_API_KEY")
#     )

#     # Make Gemini call
#     response = gemini_client.models.generate_content(
#         model="gemini-2.5-flash",
#         contents="langfuse is better or langsmith",
#     )

#     print(response.text)

#     # Make sure trace is sent to Langfuse
#     langfuse.flush()


# if __name__ == "__main__":
#     main()




import os
from dotenv import load_dotenv
from google import genai
from langsmith import wrappers

load_dotenv()


def main():
    # Pass the loaded key into the client
    gemini_client = genai.Client(
        api_key=os.getenv("GEMINI_API_KEY")
    )

    # Wrap the Gemini client for LangSmith tracing
    client = wrappers.wrap_gemini(
        gemini_client,
        tracing_extra={
            "tags": ["gemini", "python"],
            "metadata": {
                "integration": "google-genai",
            },
        },
    )

    # Make a traced Gemini call
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Explain quantum computing in simple terms.",
    )

    print(response.text)


if __name__ == "__main__":
    main()

