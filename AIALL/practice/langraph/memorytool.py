import getpass
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langfuse import Langfuse
from langfuse.langchain import CallbackHandler

# 1. Load environment variables
load_dotenv()

def set_env(var: str):
    if not os.environ.get(var):
        os.environ[var] = getpass.getpass(f"{var}: ")

set_env("GEMINI_API_KEY")
set_env("LANGFUSE_PUBLIC_KEY")
set_env("LANGFUSE_SECRET_KEY")
set_env("LANGFUSE_HOST")

# 2. Initialize Langfuse client and callback handler for LangChain
langfuse = Langfuse()
print("Langfuse auth:", langfuse.auth_check())

langfuse_handler = CallbackHandler()

# 3. Initialize Gemini via LangChain
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.environ["GEMINI_API_KEY"],
)

# 4. Structured Output
class SearchQuery(BaseModel):
    search_query: str = Field(..., description="Query optimized for web search.")
    justification: str = Field(..., description="Why this query is relevant to the request.")

structured_llm = llm.with_structured_output(SearchQuery)

output = structured_llm.invoke(
    "How does calcium CT score relate to high cholesterol?",
    config={"callbacks": [langfuse_handler]}
)

print("STRUCTURED OUTPUT:")
print(output)

# 5. Tool Calling
@tool
def multiply(a: int, b: int) -> int:
    """Multiply two integers."""
    return a * b

llm_with_tools = llm.bind_tools([multiply])

msg = llm_with_tools.invoke(
    "What is 2 times 3?",
    config={"callbacks": [langfuse_handler]}
)

print("\nTOOL CALL:")
print(msg.tool_calls)

if msg.tool_calls:
    tool_call = msg.tool_calls[0]
    result = multiply.invoke(tool_call["args"])
    print(f"Tool execution result: {result}")

# 6. Flush all pending traces to the Langfuse server before exit
# Flush using the Langfuse client instance:
langfuse.flush()